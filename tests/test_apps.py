import os
import delegator
import shutil
import util

apps = [
    ("pointwise", "0,0"),
    ("conv_1_2", "1,0"),
    ("conv_2_1", "10,0"),
    ("conv_3_1", "20,0"),
    ("conv_bw", "130,0"),
]

def pytest_generate_tests(metafunc):
    if 'app' in metafunc.fixturenames:
        metafunc.parametrize("app", apps)

def test_app(app, with_trace, force_verilate, rtl_directory):
    test, delay = app
    trace = ""
    if with_trace:
        trace = " --trace"
    util.run(f"python ../generate_harness.py"
                f" --pnr-io-collateral {test}/{test}.io.json"
                f" --bitstream {test}/{test}_pnr_bitstream"
                f" --use-jtag"
                + trace +
		f" --verify-config"
                f" --max-clock-cycles 5000000"
                f" --output-file-name harness.cpp")
    
    force = ""
    if force_verilate:
        force = " --force"
    # Verilator wrapper that only builds if the output object is not present
    # (override with --force-rebuild)
    util.run(f"python ../verilate.py" 
                f" --harness harness.cpp" 
                + force
                + trace +
                f" --verilog-directory {rtl_directory}" 
                f" --output-directory build" 
                f" --top-module-name top")

    util.run(f"make --silent -C build -j -f Vtop.mk Vtop")

    # HACK: Input file name to inpurt port file name, also pre-processing input
    # file for DELAY
    util.run(f"python ../../process_input.py ../{test}/{test}.io.json ../{test}/{test}_input.raw {delay}", cwd="build")

    util.run("./Vtop", cwd="build")

    # HACK: Output port file name to output file name, also post-processing
    # output file for DELAY
    util.run(f"python ../../process_output.py ../{test}/{test}.io.json {test}_CGRA_out.raw {test} {delay}", cwd="build")

    util.run(f"cmp {test}_CGRA_out.raw ../{test}/{test}_halide_out.raw", cwd="build")
