read_liberty /home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef /home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_def /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/routed.def
create_clock -name clk -period 0.5 [get_ports CK]
check_placement -verbose
write_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase0/reentry.v
write_db /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase0/reentry.odb
puts "REENTRY_OK"
exit
