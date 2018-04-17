#include <iostream>
#include <fstream>
#include "Vtop.h"
#include "verilated.h"
#include "jtagdriver.h"


using namespace std;

#define P(val) ((uint64_t) val)

int main(int argc, char **argv) {
  
  Verilated::commandArgs(argc, argv);
  Vtop* top = new Vtop;

  JTAGDriver* jtag = new JTAGDriver(top);
  
  jtag->reset();
  jtag->write_config_data(15);
  cout << P(top->config_data_out) << endl;
  cout << P(top->config_data_out) << endl;

} 
