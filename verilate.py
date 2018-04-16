import argparse
import delegator
import os

parser = argparse.ArgumentParser(description='Verilator wrapper')
parser.add_argument('--top-module-name', help="Top module name")
parser.add_argument('--harness', help="Path to harness file")
parser.add_argument('--verilog-directory', help="Directory containing verilog files to include in the verilator command")
parser.add_argument('--force-rebuild', help="Run verilator even if there's an existing binary", action='store_true')
parser.add_argument('--output-directory', help="Directory to place verilator output files", default="obj_dir")

args = parser.parse_args()

if os.path.isfile(f"./{args.output_directory}/V{args.top_module_name}") and not args.force_rebuild:
    print("Found an existing verilator binary, skipping")
    exit(0)
else:

    verilator_flags = ""
    if args.verilog_directory is not None:
        verilator_flags += f" -I{args.verilog_directory}"

    verilator_flags += f" -Mdir {args.output_directory}"

    def run(command):
        print(f"+ {command}")
        delegator.run(command)
    run(f"verilator{verilator_flags} -Wno-fatal --cc {args.top_module_name} --exe {args.harness} --top-module {args.top_module_name} ")

