\
set PLATFORM "/home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd"
set NETLIST  "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/strict_area_search_20261113/runs/PAIR_096_113/routed.v"
set SPEF     "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/strict_area_search_20261113/runs/PAIR_096_113/routed.spef"
set TOP      s382
set PERIOD   0.5
set CLK_PORT CK

read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog $NETLIST
link_design $TOP
create_clock -name clk -period $PERIOD [get_ports $CLK_PORT]
read_spef $SPEF

# sta::worst_slack_cmd returns SECONDS; report_tns reports NANOseconds.
puts "ROUTED_WNS_MAX [sta::worst_slack_cmd max]"
puts "ROUTED_WNS_MIN [sta::worst_slack_cmd min]"
puts "ROUTED_TNS_BEGIN"
report_tns
puts "ROUTED_TNS_END"
puts "ROUTED_STA_OK"

report_check_types -max_slew -max_capacitance -violators -digits 9
report_worst_slack -min -digits 9
report_tns -digits 9

report_checks -path_delay max -format full_clock_expanded -group_path_count 5 -digits 9
report_checks -path_delay min -format full_clock_expanded -group_path_count 5 -digits 9
