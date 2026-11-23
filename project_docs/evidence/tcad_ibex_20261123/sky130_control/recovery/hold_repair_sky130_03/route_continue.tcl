read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib}
set expected_new_buffers 10
read_db {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_dry_root_02/dry.odb}
read_sdc {/home/toylog/faeco_tcad_ibex_20261123/control_sky130/results/sky130hd/ibex/base/6_final.sdc}
if {[llength [all_clocks]] != 2} { error "Missing original two clocks" }
source {/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/setRC.tcl}
set ::env(MIN_ROUTING_LAYER) met1
set ::env(MIN_CLK_ROUTING_LAYER) met3
set ::env(MAX_ROUTING_LAYER) met5
source {/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/fastroute.tcl}
source {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/inventory_utils.tcl}
set fillers_masters {sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4 sky130_fd_sc_hd__fill_8}
set original_fillers [dict create]
foreach inst [[ord::get_db_block] getInsts] {
    if {[[$inst getMaster] getName] in $fillers_masters} {
        dict set original_fillers [$inst getName] 1
    }
}
puts "HOLD_REPAIR_FILLERS_TO_REMOVE [dict size $original_fillers]"
if {[dict size $original_fillers] != 21936} { error "unexpected physical filler count in _02 continuation" }
remove_fillers
puts HOLD_REPAIR_LEGALIZATION_START
detailed_placement
check_placement -verbose
set source [open {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/original_inventory.txt} r]
set original_insts [dict create]
set original_nets [dict create]
while {[gets $source line] >= 0} {
    lassign $line kind name state
    if {$kind eq "instance"} { dict set original_insts $name $state }
    if {$kind eq "net"} { dict set original_nets $name $state }
}
close $source
if {[dict size $original_insts] == 0 || [dict size $original_nets] == 0} { error "empty original inventory" }
set block [ord::get_db_block]
set moved [dict create]
set inserted 0
set removed 0
foreach inst [$block getInsts] {
    set name [$inst getName]
    if {![dict exists $original_insts $name]} {
        incr inserted
        dict set moved $name new
        puts "HOLD_REPAIR_INSERTED $name [instance_state $inst]"
    } elseif {[instance_state $inst] ne [dict get $original_insts $name]} {
        dict set moved $name moved
        puts "HOLD_REPAIR_MOVED $name [dict get $original_insts $name] -> [instance_state $inst]"
    }
}
dict for {name state} $original_insts {
    if {[$block findInst $name] eq "NULL" && ![dict exists $original_fillers $name]} { incr removed }
}
puts "HOLD_REPAIR_INSTANCE_DELTA inserted=$inserted removed=$removed moved=[expr {[dict size $moved] - $inserted}]"
if {$inserted != $expected_new_buffers || $removed != 0} { error "dry repair additions differ from the recorded incremental count" }
set cleared 0
set unchanged 0
set affected 0
foreach net [$block getNets] {
    if {[$net getSigType] in {POWER GROUND}} { continue }
    set name [$net getName]
    set pins [connection_state $net]
    set changed [expr {![dict exists $original_nets $name] || $pins ne [dict get $original_nets $name]}]
    foreach pin [$net getITerms] {
        if {[dict exists $moved [[$pin getInst] getName]]} { set changed 1 }
    }
    set wire [$net getWire]
    if {$changed} {
        incr affected
        puts "HOLD_REPAIR_AFFECTED_NET $name"
        if {$wire ne "NULL"} { odb::dbWire_destroy $wire; incr cleared }
    } elseif {$wire ne "NULL"} {
        incr unchanged
    }
}
if {$affected == 0 || $cleared == 0 || $unchanged == 0} { error "unexpected affected-net or existing-wire count" }
puts "HOLD_REPAIR_WIRE_DELTA affected=$affected cleared=$cleared retained_before_drt=$unchanged"
pin_access
puts HOLD_REPAIR_GRT_START
global_route
set endpoint {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint}
puts HOLD_REPAIR_DRT_START
set route_args {-verbose 1 -droute_end_iter 64}
detailed_route -output_drc $endpoint/drc_initial.rpt {*}$route_args
set drc [detailed_route_num_drvs]
puts "HOLD_REPAIR_DRT_INITIAL_VIOLATIONS $drc"
if {![design_is_routed]} { error "Unrouted nets after hold DRT" }
if {$drc != 0} { error "DRC violations after hold DRT" }
check_placement -verbose
set report $endpoint/antenna_initial.rpt
set antenna [check_antennas -report_file $report]
puts "HOLD_REPAIR_ANTENNA_INITIAL_VIOLATIONS $antenna"
set round 0
set drc_report $endpoint/drc_initial.rpt
while {$antenna > 0 && $round < 2} {
    incr round
    puts "HOLD_REPAIR_ANTENNA_ROUND_START $round violations=$antenna"
    set diodes [repair_antennas -iterations 1 -diode_only]
    puts "HOLD_REPAIR_ANTENNA_DIODE_TOTAL $diodes"
    if {$diodes <= 0} { break }
    check_placement -verbose
    set drc_report $endpoint/drc_antenna_$round.rpt
    detailed_route -output_drc $drc_report {*}$route_args
    set drc [detailed_route_num_drvs]
    puts "HOLD_REPAIR_ANTENNA_ROUND_DRC $round violations=$drc"
    if {![design_is_routed]} { error "Unrouted nets after antenna DRT" }
    if {$drc != 0} { error "DRC violations after antenna DRT" }
    set report $endpoint/antenna_$round.rpt
    set antenna [check_antennas -report_file $report]
    puts "HOLD_REPAIR_ANTENNA_ROUND_END $round violations=$antenna"
}
file copy $drc_report $endpoint/drc.rpt
puts "HOLD_REPAIR_DRT_VIOLATIONS $drc"
puts HOLD_REPAIR_DRT_COMPLETE
filler_placement $fillers_masters
check_placement -verbose
puts HOLD_REPAIR_FILLERS_RESTORED
set antenna [check_antennas -report_file $endpoint/antenna.rpt]
puts "HOLD_REPAIR_ANTENNA_VIOLATIONS $antenna"
set ::env(REPORTS_DIR) {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint}
source {/home/toylog/faeco_eda/orfs/flow/scripts/util.tcl}
write_verilog {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/6_final.v} -remove_cells [find_physical_only_masters]
write_def {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/6_final.def}
write_db {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/6_final.odb}
write_guides {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/route.guide}
file copy {/home/toylog/faeco_tcad_ibex_20261123/control_sky130/results/sky130hd/ibex/base/6_final.sdc} {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/6_final.sdc}
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file {/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/rcx_patterns.rules}
write_spef {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/endpoint/6_final.spef}
puts HOLD_REPAIR_RCX_COMPLETE
puts HOLD_REPAIR_ROUTE_COMPLETE
exit
