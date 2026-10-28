read_liberty /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_adapter_current_pin_20261018/v2/pytest_tmp_B3/test_STA_exception_identity_an1/cells.lib
read_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_adapter_current_pin_20261018/v2/pytest_tmp_B3/test_STA_exception_identity_an1/evidence/B3_RECONSTRUCTION_RUNS/new_run/b09/mapped.v
link_design b09
create_clock -name clk -period 0.5 [get_ports CK]
report_checks -path_delay max
puts "TNS_BEGIN"
report_tns
puts "TNS_END"
report_worst_slack -max
