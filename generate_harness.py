# ❯ python generate_harness.py --pnr-io-collateral pointwise.io.json --bitstream pointwise.bs && astyle harness.cpp

import argparse
import json

parser = argparse.ArgumentParser(description='Test the cgra')
# parser.add_argument('--IO', metavar='<IO_FILE>', help='File containing mapping between IO ports and files', dest="pnr_io_collateral")
parser.add_argument('--pnr-io-collateral', metavar='<collateral_file>.io.json', help='Collateral file generated by SMT-PNR', required=True)
parser.add_argument('--bitstream', metavar='<BITSTREAM_FILE>', help='Bitstream file containing the CGRA configuration', required=True)
parser.add_argument('--trace-file', help='Trace file', dest="trace_file", default=None)
parser.add_argument('--max-clock-cycles', help='Max number of clock cyles to run', dest="max_clock_cycles", default=40, type=int)
parser.add_argument('--wrapper-module-name', help='Name of the wrapper module', default='CGRA_wrapper')

args = parser.parse_args()

config_data_arr = []
config_addr_arr = []

with open(args.bitstream, "r") as bitstream_file:
    for line in bitstream_file:
        config_addr, config_data = line.split()
        config_addr_arr.append(f"0x{config_addr}")
        config_data_arr.append(f"0x{config_data}")

config_data_arr_str = "{" + ", ".join(config_data_arr) + "}"
config_addr_arr_str = "{" + ", ".join(config_addr_arr) + "}"

with open(args.pnr_io_collateral, "r") as pnr_collateral:
    io_collateral = json.load(pnr_collateral)

# with open(args.IO, "r") as IO_file:
#     """
#     { 
#         "<module_name>": "<file_name>",
#         "<module_name>": "<file_name>",
#         "<module_name>": "<file_name>"
#         ...
#     }
#     """
#     IOs = json.load(IO_file)

file_setup = ""
input_body = ""
output_body = ""
file_close = ""
wrapper_name = args.wrapper_module_name

# for entry in IOs:
for module in io_collateral:
    file_name = f"{module}.raw"
    mode = io_collateral[module]["mode"]
    if mode == "inout":
        raise NotImplementedError()
    file_setup += f"""
        std::fstream {module}_file("{file_name}", ios::{mode} | ios::binary);
        if (!{module}_file.is_open()) {{
            std::cout << "Could not open file {file_name}" << std::endl;
            return 1;
        }}
        uint16_t {module}_{mode} = 0;
    """

    if mode == 'in':
        input_body += f"""
            {module}_file.read(&{module}_in, sizeof(uint16_t));
            if ({module}_file.eof()) {{
                std::cout << "Reached end of file {module}_file" << std::endl;
                break;
            }}
            {wrapper_name}->{module} = {module}_in;
        """
    else:
        output_body += f"""
            {module}_out = {wrapper_name}->{module};
            {module}_file.write(&{module}_out, sizeof(uint16_t));
        """

    file_close += f"""
        {module}_file.close();
    """

harness = f"""\
#include "V{wrapper_name}.h"
#include "verilated.h"
#include <iostream>
#include <cstdint>
#include <fstream>

#define next(circuit) \\
    do {{ step((circuit)); step((circuit)); }} while (0)

static const uint32_t config_data_arr[] = {config_data_arr_str};
static const uint32_t config_addr_arr[] = {config_addr_arr_str};

// TODO: How many cycles do we actually need to hold reset down?
static const uint32_t NUM_RESET_CYCLES = 5;

void step(V{wrapper_name} *{wrapper_name}) {{
    {wrapper_name}->clk_in ^= 1;
    {wrapper_name}->eval();
}}

int main(int argc, char **argv) {{
    Verilated::commandArgs(argc, argv);
    V{wrapper_name}* {wrapper_name} = new V{wrapper_name};

    {file_setup}

    {wrapper_name}->clk_in = 0;
    {wrapper_name}->config_addr_in = 0;
    {wrapper_name}->config_data_in = 0;
    std::cout << "Initializing the CGRA by holding reset high for " << NUM_RESET_CYCLES << "cycles" << std::endl;
    {wrapper_name}->reset_in = 1;
    for (int i = 0; i < NUM_RESET_CYCLES; i++) {{
        // TODO: SR's test bench starts on negative edge
        next({wrapper_name});
    }}

    for (int i = 0; i < {len(config_data_arr)}; i++) {{
        {wrapper_name}->config_data_in = config_data_arr[i];
        {wrapper_name}->config_addr_in = config_addr_arr[i];
        next({wrapper_name});
    }}

    for (int i = 0; i < {args.max_clock_cycles}) {{
        {input_body}
        step({wrapper_name});
        {output_body}
        step({wrapper_name});
    }}

    {file_close}
}}
"""

with open("harness.cpp", "w") as harness_file:
    harness_file.write(harness)
