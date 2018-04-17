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
  private :
    Vtop* top;
    IRValue cur_ir = IR_EXTEST;
    uint32_t cur_config_data = 0;
    uint32_t cur_config_data_bits = 0;
    //ConfigOpValue cur_config_op = OP_NOP;
    uint32_t cur_config_addr = 0;
  public :
    JTAGDriver(Vtop* top) : top(top) {}

    void reset() {
      top->tck = 0;
      top->tdi = 0;
      top->tms = 0;
      top->trst_n =1;
      top->reset_in =0;
      top->eval();
      top->trst_n = 0;
      top->reset_in =1;
      top->eval();
      top->reset_in =0;
      top->trst_n = 1;
      top->eval();
      top->tck = 1;
      top->eval();
      this->step(0);
      this->step(0);
    }
    int top1(uint32_t val) {
      for (int i=31; i>=0; --i) {
        if ((val>>i)&1) return i;
      }
      return -1;
    }
    void print() {
      //cout << "--" << endl;
      ////cout << "Wr " << (uint64_t) top->write << endl;
      //cout << "addr " << (uint64_t) top->config_addr_out << endl;
      //cout << "tms " << (uint64_t) top->tms << endl;
      //cout << "tdi " << (uint64_t) top->tdi << endl;
      //cout << "tap: " << top1(top->global_controller->jtag_controller->cfg_and_dbg->tap->tap_state) << endl;
      //cout << "inst: " << (uint64_t) (top->global_controller->jtag_controller->cfg_and_dbg->tap->instruction) << endl;
      //cout << "sc_addr: " << (uint64_t) (top->global_controller->jtag_controller->cfg_and_dbg->sc_addr) << endl;
      //cout << "sc_shift: " << (uint64_t) (top->global_controller->jtag_controller->cfg_and_dbg->sc_cfg_addr_shift_dr) << endl;
      //cout << "op: " << (uint64_t) (top->global_controller->op) << endl;
      //cout << "op_en: " << (uint64_t) (top->global_controller->jtag_controller->cfg_and_dbg->inst_update_qualified) << endl;
      //cout << "inst_pre: " << (uint64_t) (top->global_controller->jtag_controller->cfg_and_dbg->tap->tap->capture_reg_ir) << endl;
    }

    //Returns 'tdo'
    uint8_t step(bool tms_val, bool tdi_val=0) {
      assert(top->tck==1);
      //Just finished posedge
      top->tck = 0;
      top->tms = (uint8_t)tms_val;
      top->tdi = (uint8_t)tdi_val;
      top->eval(); //negedge
      print();
      uint8_t tdo = top->tdo;
      top->tck = 1;
      top->eval(); //posedge
      return tdo;
    }

    void shift(uint32_t value, uint32_t bits) {
      if (bits <32) assert((value>>bits)==0); //Check only 'size' bits are set
      for (int i=0; i<bits; ++i) { //lsb first
        uint8_t tms = i==bits-1?1:0; //Exit on last
        this->step(tms,(value >> i)&1); 
      }
    }

    void write_IR(IRValue addr) {
      //if (this->cur_ir == addr) return; //"caching"
      this->step(1); //select DR
      this->step(1); //select IR
      this->step(0); //capture IR
      this->step(0); //shift IR
      this->shift((uint32_t) addr, 5); //Shift in the data and exit1
      this->step(1); //update IR
      this->step(0); // idle
      this->step(0); // idle //Need this second idle state
      
      this->cur_ir = addr;
    }

    void write_DR(uint32_t value, uint32_t bits) {
      //if (this->cur_config_data_bits == bits && this->cur_config_data == value) return;
      this->step(1); // select DR
      this->step(0); // capture DR
      this->step(0); // shift DR
      this->shift(value, bits); //shift in data, and exit1
      this->step(1); // update DR
      this->step(0); // idle
      this->step(0); // idle

      this->cur_config_data_bits = bits;
      this->cur_config_data = value;
    }

    void write_config_addr(uint32_t config_addr) {
      this->write_IR(IR_CONFIG_ADDRESS);
      this->write_DR(config_addr,32);
    }

    void write_config_data(uint32_t config_data) {
      this->write_IR(IR_CONFIG_DATA);
      this->write_DR(config_data,32);
    }

    void write_config_op(ConfigOpValue op) {
      this->write_IR(IR_CONFIG_OP);
      this->write_DR((uint32_t) op, 5);
    }

    void write_config(uint32_t addr, uint32_t data) {
      this->write_config_addr(addr);
      this->write_config_data(data);
      this->write_config_op(OP_WRITE);
    }

};
