import json
import sys
import shutil

with open(sys.argv[1], "r") as file:
    info = json.load(file)

input_file_name = sys.argv[2]

name = None
for key in info:
    if info[key]["mode"] == "in":
        assert name is None, "This only works for one in"
        name = key

assert name is not None, "We need at least one in"

shutil.copy(input_file_name, f"{name}.raw")
