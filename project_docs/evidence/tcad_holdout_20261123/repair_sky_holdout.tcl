set src $::env(FAECO_HOLDOUT_SOURCE)
set out $::env(FAECO_HOLDOUT_REPAIR)
set flow /home/toylog/faeco_eda/orfs/flow
set platform $flow/platforms/sky130hd
set corners /home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd

define_corners TT FF SS
read_liberty -corner TT $platform/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty -corner FF $corners/sky130_fd_sc_hd__ff_n40C_1v95.lib
read_liberty -corner SS $corners/sky130_fd_sc_hd__ss_n40C_1v40.lib
read_db $src/6_final.odb
read_sdc $src/6_final.sdc
if {[llength [all_clocks]] != 2} { error "Lost original core or virtual clock" }
foreach corner {TT FF SS} { read_spef -corner $corner $src/6_final.spef }
source $platform/setRC.tcl

set filler_masters {sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8}
source $::env(FAECO_HOLDOUT_INVENTORY)
set before_instances [dict create]
set before_connections [dict create]
foreach inst [[ord::get_db_block] getInsts] {
    if {[[$inst getMaster] getName] ni $filler_masters} {
        dict set before_instances [$inst getName] [instance_state $inst]
    }
}
foreach net [[ord::get_db_block] getNets] {
    if {[$net getSigType] ni {POWER GROUND}} {
        dict set before_connections [$net getName] [connection_state $net]
    }
}
remove_fillers
puts "HOLD_REPAIR_BEFORE_PS [expr {1.0e12 * [sta::worst_slack_cmd min]}]"
repair_timing -hold -hold_margin $::env(FAECO_HOLDOUT_MARGIN_NS) -max_buffer_percent 10 -allow_setup_violations
puts "HOLD_REPAIR_ESTIMATE_PS [expr {1.0e12 * [sta::worst_slack_cmd min]}]"
detailed_placement
check_placement -verbose

set block [ord::get_db_block]
set changed_instances [dict create]
set added 0
foreach inst [$block getInsts] {
    set name [$inst getName]
    set present [dict exists $before_instances $name]
    if {!$present} { incr added }
    if {!$present || [dict get $before_instances $name] ne [instance_state $inst]} {
        dict set changed_instances $name 1
    }
}
dict for {name state} $before_instances {
    if {[$block findInst $name] eq "NULL"} { error "Existing non-filler instance removed: $name" }
}
if {$added <= 0} { error "No repair buffers added" }
puts "HOLD_REPAIR_INSTANCES added=$added changed=[dict size $changed_instances]"

set wires 0
set retained 0
foreach net [$block getNets] {
    if {[$net getSigType] in {POWER GROUND}} { continue }
    set name [$net getName]
    set changed [expr {![dict exists $before_connections $name] || [dict get $before_connections $name] ne [connection_state $net]}]
    foreach pin [$net getITerms] {
        if {[dict exists $changed_instances [[$pin getInst] getName]]} { set changed 1 }
    }
    set wire [$net getWire]
    if {$wire eq "NULL"} { continue }
    if {$changed} { odb::dbWire_destroy $wire; incr wires } else { incr retained }
}
if {$wires == 0 || $retained == 0} { error "Expected both cleared and preserved wires" }
puts "HOLD_REPAIR_WIRES cleared=$wires retained=$retained"

set ::env(MIN_ROUTING_LAYER) met1
set ::env(MIN_CLK_ROUTING_LAYER) met3
set ::env(MAX_ROUTING_LAYER) met5
source $::env(FAECO_HOLDOUT_FASTROUTE)
pin_access
global_route
set route_args {-verbose 1 -droute_end_iter 64}
detailed_route -output_drc $out/drc_initial.rpt {*}$route_args
set drc_report $out/drc_initial.rpt
set antenna [check_antennas -report_file $out/antenna_initial.rpt]
for {set round 1} {$round <= 2 && $antenna > 0} {incr round} {
    if {[repair_antennas -iterations 1 -diode_only] <= 0} { break }
    check_placement -verbose
    set drc_report $out/drc_antenna_$round.rpt
    detailed_route -output_drc $drc_report {*}$route_args
    set antenna [check_antennas -report_file $out/antenna_$round.rpt]
}
if {![design_is_routed] || [detailed_route_num_drvs] != 0 || $antenna != 0} {
    error "Ineligible hold repair route: drc=[detailed_route_num_drvs], antenna=$antenna"
}
file copy $drc_report $out/drc.rpt
filler_placement $filler_masters
check_placement -verbose
set ::env(REPORTS_DIR) $out
source $flow/scripts/util.tcl
write_verilog $out/6_final.v -remove_cells [find_physical_only_masters]
write_def $out/6_final.def
write_db $out/6_final.odb
write_guides $out/route.guide
file copy $src/6_final.sdc $out/6_final.sdc
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $platform/rcx_patterns.rules
write_spef $out/6_final.spef
puts HOLD_REPAIR_ROUTE_AND_RCX_COMPLETE
exit
