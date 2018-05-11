import delegator


with open("pointwise_input.raw", "rb") as input_file:
    with open("expected_output.raw", "wb") as output_file:
        byte = input_file.read(1)
        while byte != b"":
            output_file.write(bytes([byte[0] * 2 & 0xFF]))
            byte = input_file.read(1)

assert not delegator.run("cmp expected_output.raw pointwise_halide_out.raw").return_code
