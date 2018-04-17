rm -rf obj_dir
verilator top.sv --cc vlog/* --exe tb.cpp -CFLAGS -std=c++11;
make -C obj_dir -f Vtop.mk Vtop;
./obj_dir/Vtop;
