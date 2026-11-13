\
set PLATFORM "/home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd"
set ORFS     "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629"
set NETLIST  "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/experiments/20261016_r22_cut_ablation_v3/W1/s382/mapped.v"
set OUTDIR   "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382"
set TOP      s382
set PERIOD   0.5
set UTIL     0.35
set DENSITY  0.55
set CLK_PORT CK
set DROUTE_ITER 15

read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef $PLATFORM/lef/sky130_fd_sc_hd.tlef
read_lef $PLATFORM/lef/sky130_fd_sc_hd_merged.lef
read_verilog $NETLIST
link_design $TOP
create_clock -name clk -period $PERIOD [get_ports $CLK_PORT]

initialize_floorplan -utilization $UTIL -aspect_ratio 1.0 -core_space 2.0 -site unithd
make_tracks
place_pins -hor_layers met3 -ver_layers met2
source $PLATFORM/pdn.tcl
tapcell -distance 14 -tapcell_master sky130_fd_sc_hd__tapvpwrvgnd_1
global_placement -density $DENSITY
detailed_placement
clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8} -root_buf sky130_fd_sc_hd__clkbuf_16
repair_clock_nets
detailed_placement
write_def $OUTDIR/cts.def
set_propagated_clock [all_clocks]

source $ORFS/setRC.tcl
set_routing_layers -signal met1-met5 -clock met3-met5
# ---- FAECO-P P1: OpenROAD resizer ----
# Runs after setRC.tcl/set_routing_layers, before routing.
# Legalising the resizer's new cells is necessary for DRT to find pins.
repair_timing -setup
detailed_placement
# ----------------------------------------
pin_access
global_route
detailed_route -output_drc $OUTDIR/drc.rpt -verbose 0 -droute_end_iter $DROUTE_ITER
write_def $OUTDIR/routed.def
write_verilog $OUTDIR/routed.v

define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $ORFS/rcx/rcx_patterns.rules
write_spef $OUTDIR/routed.spef
puts "ROUTED_FLOW_OK"
