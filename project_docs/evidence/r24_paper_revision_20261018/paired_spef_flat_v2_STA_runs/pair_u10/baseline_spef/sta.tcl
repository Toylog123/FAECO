read_liberty /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r24_paper_revision_20261018/paired_spef_flat_v2/generated/baseline.flat.v
link_design s382
read_spef /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/r24_paper_revision_20261018/paired_spef_flat_v2_STA_runs/pair_u10/baseline.spef
create_clock -name clk -period 0.5 [get_ports CK]
report_checks -path_delay max
report_worst_slack -max
report_worst_slack -min