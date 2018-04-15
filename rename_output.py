import json
import sys
import delegator

with open(sys.argv[1], "r") as file:
    info = json.load(f)

target_file_name = sys.argv[2]

name = None
for key in info:
    if info[key]["mode"] == "out":
        assert name is None, "This only works for one output"
        name = key

assert name is not None, "We need at least one output"

delegator.run(f"cp {name}.raw {target_file_name}")
