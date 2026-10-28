read_liberty /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_adapter_current_pin_20261018/v2/pytest_tmp_B3/test_candidate_launch_commit_a2/cells.lib
read_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r22_adapter_current_pin_20261018/v2/pytest_tmp_B3/test_candidate_launch_commit_a2/evidence/B3_RECONSTRUCTION_RUNS/new_run/b09/eval/iter001_cand001/000_g_G/mapped.v
link_design b09
create_clock -name clk -period 0.5 [get_ports CK]
report_worst_slack -max
