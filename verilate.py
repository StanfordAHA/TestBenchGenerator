import argparse
import delegator
import os

parser = argparse.ArgumentParser(description='Verilator wrapper')
parser.add_argument('--top-module-name', help="Top module name")
parser.add_argument('--harness', help="Path to harness file")
parser.add_argument('--verilog-directory', help="Directory containing verilog files to include in the verilator command")
parser.add_argument('--force-rebuild', help="Run verilator even if there's an existing binary", action='store_true')
parser.add_argument('--output-directory', help="Directory to place verilator output files", default="obj_dir")
parser.add_argument('--trace', action="store_true", help="Dump a .vcd using verilator")

args = parser.parse_args()

if os.path.isfile(f"./{args.output_directory}/V{args.top_module_name}.mk") and not args.force_rebuild:
    print("Found an existing verilator binary, skipping")
    exit(0)
else:

    verilator_flags = ""
    if args.verilog_directory is not None:
        verilator_flags += f" -I{args.verilog_directory}"
    if args.trace:
        verilator_flags += " --trace"

    verilator_flags += f" -Mdir {args.output_directory}"
    if args.trace:
        verilator_flags += f" -CFLAGS '-std=c++11 -DTRACE'"
    else:
        verilator_flags += f" -CFLAGS -std=c++11"

    def run(command):
        print(f"+ {command}")
        result = delegator.run(command)
        print(result.out)
        if result.return_code:
            print(result.err)
            raise RuntimeError(f"ERROR - running command {command}")
    run(f"verilator{verilator_flags} -Wno-fatal --cc {args.top_module_name} --exe {args.harness} --top-module {args.top_module_name} ")

