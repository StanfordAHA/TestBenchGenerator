import json
import sys
import shutil

with open(sys.argv[1], "r") as file:
    info = json.load(file)

target_file_name = sys.argv[2]
app = sys.argv[3]
delay_in, delay_out = [int(x) for x in sys.argv[4].split(",")]

name = None
for key in info:
    if info[key]["mode"] == "out":
        assert name is None, "This only works for one output"
        name = key

assert name is not None, "We need at least one output"

if delay_in:
    print(delay_in)
    with open(f"{name}.raw", "rb") as output_file:
        output_file.seek(delay_in)
        output_data = output_file.read()
    with open(f"{name}.raw", "wb") as output_file:
        output_file.write(output_data)

# TODO: Why do we we do this post processing for these apps?
if app == "conv_1_2":
    import delegator
    print(f"bin/conv_1_2_convert < {name}.raw > {target_file_name}")
    print(delegator.run(f"bin/conv_1_2_convert < {name}.raw > {target_file_name}").return_code)
elif app == "conv_bw":
    import delegator
    delegator.run(f"bin/crop31 < {name}.raw > {target_file_name}")
else:
    shutil.copy(f"{name}.raw", target_file_name)
