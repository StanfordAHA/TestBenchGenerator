#!/bin/bash

set -eux

python wrap_cgra.py --pnr-io-collateral pointwise.io.json --cgra-verilog top.v
python generate_harness.py --pnr-io-collateral pointwise.io.json --bitstream pointwise.bs --max-clock-cycles 5000000

# png to raw
./myconvert.csh inputs/pointwise.png io16in_in_arg_1_0_0.raw
./myconvert.csh gold_outputs/pointwise.png gold_output.raw

VERILATOR_TOP=../CGRAFlow/CGRAGenerator/verilator/generator_z_tb/


RTL_DIR=../CGRAFlow/CGRAGenerator/hardware/generator_z/top/genesis_verif/

cp $VERILATOR_TOP/sram_stub.v $RTL_DIR/sram_512w_16b.v  # SRAM hack
cp CGRA_wrapper.v $RTL_DIR

# verilator -I$RTL_DIR -Wno-fatal --cc CGRA_wrapper --exe harness.cpp --top-module CGRA_wrapper
make --silent -C obj_dir -j -f VCGRA_wrapper.mk VCGRA_wrapper -B
./obj_dir/VCGRA_wrapper

cmp io16_out_0_0.raw gold_output.raw
