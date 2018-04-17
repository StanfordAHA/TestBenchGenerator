//  input  tck;
//  input  clk_in;
//  input  reset_in;
//  input  tdi;
//  input  tms;
//  input  trst_n;
//  input [31:0] config_data_in;

class JTAGDriver {
  public:
    enum IRValue {
      IR_EXTEST=0,
      IR_IDCODE=1,
      IR_SAMPLE=2,
      IR_CONFIG_DATA=8,
      IR_CONFIG_OP=9,
      IR_CONFIG_ADDRESS=10,
      IR_BYPASS=31,
    };

    enum ConfigOpValue {
      OP_NOP=0,
      OP_WRITE=1,
      OP_READ=2,
      OP_WRITE_TST=8,
      OP_READ_TST=9,
      OP_GLOBAL_RESET=10,
      OP_WRITE_STALL=11,
      OP_READ_STALL=12,
      OP_SWITCH_TO_SYS_CLK=15,
      OP_WRITE_RD_DELAY_REG=16,
      OP_READ_RD_DELAY_REG=17
    };
    Vtop* top;
    IRValue cur_ir = IR_EXTEST;
    uint32_t cur_config_data = 0;
    ConfigOpValue cur_config_op = OP_NOP;
    uint32_t cur_config_addr = 0;
    JTAGDriver(Vtop* top) : top(top) {}

    void reset() {
      top->tck = 0;
      top->tdi = 0;
      top->tms = 0;
      top->trst_n =1;
      top->eval();
      top->trst_n = 0;
      top->eval();
      top->trst_n = 1;
      top->eval();
      top->tck = 1;
      top->eval();
      this->step(0);
      this->step(0);
    }
    void step(bool tms_val, bool tdi_val=0) {
      assert(top->tck==1);
      //Just finished posedge
      top->tck = 0;
      top->tms = (uint8_t)tms_val;
      top->tdi = (uint8_t)tdi_val;
      top->eval(); //negedge
      top->tck = 1;
      top->eval(); //posedge
    }
    void shift(uint32_t value, int32_t bits) {
      if (bits <32) assert((value>>bits)==0); //Check only 'size' bits are set
      for (int i=0; i<bits; ++i) { //lsb first
      //for (int i=bits-1; i>=0; --i) { //msb first
        this->step(0,(value << i)&1); 
      }
    }
    void write_IR(IRValue addr) {
      this->step(1); //select DR
      this->step(1); //select IR
      this->step(0); //capture IR
      this->step(0); //shift IR
      this->shift((uint32_t) addr, 5); //Shift in the data
      this->step(1); //Exit1 IR
      this->step(1); //update IR
      this->step(0); // idle
    }

    void write_DR(uint32_t value, int size) {
      this->step(1); // select DR
      this->step(0); // capture DR
      this->step(0); // shift DR
      this->shift(value, size); //shift in data
      this->step(1); // exit1 DR
      this->step(1); // update DR
      this->step(0); // idle
    }

    void write_config_addr(uint32_t config_addr) {
      this->write_IR(IR_CONFIG_ADDRESS);
      this->write_DR(config_addr,32);
    }

    void write_config_data(uint32_t config_data) {
      this->write_IR(IR_CONFIG_ADDRESS);
      this->write_DR(config_data,32);
    }

    void write_config_op(ConfigOpValue op) {
      this->write_IR(IR_CONFIG_OP);
      this->write_DR((uint32_t) op, 5);
    }

};
