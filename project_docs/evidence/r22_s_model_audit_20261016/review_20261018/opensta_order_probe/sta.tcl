read_liberty /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_s_model_audit_20261016/review_20261018/not_executed_mapped.v
link_design top
create_clock -name clk -period 0.5 [get_ports CK]
report_checks -path_delay max
read_spef /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_s_model_audit_20261016/review_20261018/not_executed.spef
puts "TNS_BEGIN"
report_tns
puts "TNS_END"
report_worst_slack -max
report_worst_slack -min
