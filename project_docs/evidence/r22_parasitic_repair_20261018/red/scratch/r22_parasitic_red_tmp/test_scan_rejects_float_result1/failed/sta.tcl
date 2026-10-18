read_liberty D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_red_tmp\test_scan_rejects_float_result1\test.lib
read_verilog D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\r22_parasitic_red_tmp\test_scan_rejects_float_result1\baseline.v
link_design top
create_clock -name clk -period 0.5 [get_ports CK]
report_checks -path_delay max
report_worst_slack -max
report_worst_slack -min