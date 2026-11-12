read_liberty /home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_db /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase0/reentry.odb
create_clock -name clk -period 0.5 [get_ports CK]
set_propagated_clock [all_clocks]
source /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/setRC.tcl
read_spef /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/routed.spef

detailed_placement
check_placement -verbose
set_routing_layers -signal met1-met5 -clock met3-met5
set cleared 0
foreach net [[ord::get_db_block] getNets] {
    if {[$net getSigType] in {POWER GROUND}} { continue }
    set wire [$net getWire]
    if {$wire ne "NULL"} { odb::dbWire_destroy $wire; incr cleared }
}
puts "CLEARED_SIGNAL_WIRES $cleared"
pin_access
global_route
detailed_route -output_drc /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase1_v2/CONTROL/drc.rpt -verbose 0 -droute_end_iter 15
check_placement -verbose
write_verilog /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase1_v2/CONTROL/routed.v
write_def /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase1_v2/CONTROL/routed.def
write_db /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase1_v2/CONTROL/routed.odb
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/rcx/rcx_patterns.rules
write_spef /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/recovery_qualification_20261112/phase1_v2/CONTROL/routed.spef
puts "PHYSICAL_PROBE_OK"
exit
