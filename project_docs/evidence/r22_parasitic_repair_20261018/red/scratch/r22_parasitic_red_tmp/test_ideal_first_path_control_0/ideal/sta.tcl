read_liberty D:\BaiduSyncdisk\01_Papers\03_FAECO\data\raw\benchmarks\raw\openroad_flow_scripts_sky130hd\da8f092a02a8e75658cc3100691aabff05f35629\lib\sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_red_tmp\test_ideal_first_path_control_0\baseline.v
link_design top
create_clock -name clk -period 0.5 [get_ports CK]
report_checks -path_delay max
puts "TNS_BEGIN"
report_tns
puts "TNS_END"
report_worst_slack -max
report_worst_slack -min
