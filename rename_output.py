import json
import sys
import shutil

with open(sys.argv[1], "r") as file:
    info = json.load(file)

target_file_name = sys.argv[2]
app = sys.argv[3]
delay_in, delay_out = sys.argv[4].split(",")

name = None
for key in info:
    if info[key]["mode"] == "out":
        assert name is None, "This only works for one output"
        name = key

assert name is not None, "We need at least one output"

if delay_in:
    with open(f"{name}.raw", "r+wb") as output_file:
        output_file.write(output_file[delay_in:])

# TODO: Why do we we do this post processing for these apps?
if app in ["conv_1_2"]:
    import delegator
    delegator.run(f"../CGRAGenerator/verilator/generator_z_tb/bin/{app}_convert < {name}.raw > {target_file_name}")
else:
    shutil.copy(f"{name}.raw", target_file_name)
