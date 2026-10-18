read_liberty D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_green4_tmp\test_scan_respects_explicit_cl0\test.lib
read_verilog D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_green4_tmp\test_scan_respects_explicit_cl0\repaired.v
link_design top
read_spef D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_green4_tmp\test_scan_respects_explicit_cl0\clocked\repaired.spef
create_clock -name clk -period 0.75 [get_ports alternate_clk]
report_checks -path_delay max
report_worst_slack -max
report_worst_slack -min