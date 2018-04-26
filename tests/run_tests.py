import os
import delegator
import argparse
import shutil

def run(cmd, cwd="."):
    print("+ " + cmd)
    result = delegator.run(cmd, cwd=cwd)
    print(result.out)
    if result.return_code:
        print(result.err)
        raise RuntimeError()
    return result


parser = argparse.ArgumentParser(description='Test the cgra')
parser.add_argument("--rtl-directory", help="Path to top.v", required=True)
parser.add_argument('--files-to-copy', nargs='+', help='Files to copy to rtl-directory')
parser.add_argument('--trace', action="store_true")
parser.add_argument('--force-verilate', action="store_true")

args = parser.parse_args()

for file in args.files_to_copy:
    shutil.copy(file,  f"{args.rtl_directory}/")

shutil.copy("../jtag/jtagdriver.h", "build/")

run("cc conv_1_2_convert.c -o conv_1_2_convert", cwd="../bin")
run("cc crop31.c -o crop31", cwd="../bin")

for test, delay in [
        ("pointwise", "0,0"),
        # ("conv_1_2", "1,0"),
        # ("conv_2_1", "10,0"),
        # ("conv_3_1", "20,0"),
        # ("conv_bw", "130,0"),
    ]:
    run(f"""python ../generate_harness.py \\
                --pnr-io-collateral {test}/{test}.io.json      \\
                --bitstream {test}/{test}_pnr_bitstream        \\
                --use-jtag       \\
		--verify-config                           \
                --max-clock-cycles 5000000                \\
                --output-file-name harness.cpp
        """)
    
    force = ""
    if args.force_verilate:
        force = " --force"
    # Verilator wrapper that only builds if the output object is not present
    # (override with --force-rebuild)
    run(f"python ../verilate.py" 
                f" --harness harness.cpp" 
                + force +
                f" --verilog-directory {args.rtl_directory}" 
                f" --output-directory build" 
                f" --top-module-name top")

    trace_flag = ""
    if args.trace:
        trace_flag = " -DTRACE"
    run(f"make --silent -C build -j -f Vtop.mk Vtop {trace_flag}")

    # HACK: Input file name to inpurt port file name, also pre-processing input
    # file for DELAY
    run(f"python ../../process_input.py ../{test}/{test}.io.json ../{test}/{test}_input.raw {delay}", cwd="build")

    run("./Vtop", cwd="build")

    # HACK: Output port file name to output file name, also post-processing
    # output file for DELAY
    run(f"python ../../process_output.py ../{test}/{test}.io.json {test}_CGRA_out.raw {test} {delay}", cwd="build")
