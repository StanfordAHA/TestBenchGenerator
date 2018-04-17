#include <iostream>
#include <fstream>
#include <vector>
#include "Vtop.h"

//These following includes are only needed for debugging
#include "Vtop_global_controller.h"
#include "Vtop_jtag_unq1.h"
#include "Vtop_cfg_and_dbg_unq1.h"
#include "Vtop_tap_unq1.h"
#include "Vtop_DW_tap__W5_I1_S1.h"

#include "verilated.h"
#include "jtagdriver.h"


using namespace std;

//Need if you are passing to cout
#define cast(val) ((uint32_t) val)

int main(int argc, char **argv) {
  
  Verilated::commandArgs(argc, argv);
  Vtop* top = new Vtop;

  JTAGDriver* jtag = new JTAGDriver(top);
  
  jtag->reset();
  
  cout << "Testing Write op" << endl;
  jtag->write_config_op(JTAGDriver::OP_WRITE);
  assert(top->write==1);
  
  cout << "Testing cgra writes" << endl;
  vector<std::pair<uint32_t,uint32_t>> testconfigs({
    {123,456},
    {0xaaaaaaaa,0x55555555},
    {0xffffffff,0x99999999},
    {0xabcdef12,0x01234567}
  });
  for (auto config : testconfigs) {
    uint32_t addr = config.first;
    uint32_t data = config.second;
    jtag->write_config(addr,data);
    assert(top->write==1);
    assert(top->config_addr_out==addr);
    assert(top->config_data_out==data);
  }
  
  cout << "Testing cgra reads" << endl;
  for (auto config : testconfigs) {
    uint32_t addr = config.first;
    uint32_t data = config.second;
    top->config_data_in = data;
    uint32_t data_check = jtag->read_config(addr);
    assert(data_check==data);
  }

  cout << "Success!!!" << endl;
} 
