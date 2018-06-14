import json
import sys
import shutil

with open(sys.argv[1], "r") as file:
    info = json.load(file)

input_file_name = sys.argv[2]
delay_in, delay_out = [int(x) for x in sys.argv[3].split(",")]

name = None
for key in info:
    if info[key]["mode"] == "in":
        assert name is None, "This only works for one in"
        name = key

assert name is not None, "We need at least one in"

if delay_out:
    with open(input_file_name, "rb") as input_file:
        with open(f"{name}.raw", "wb") as output_file:
            output_file.write(input_file.read())
            for i in range(delay_out):
                output_file.write(b'\0')
else:
    shutil.copy(input_file_name, f"{name}.raw")

