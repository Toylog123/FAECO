read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib}
read_db {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_02/endpoint/6_final.odb}
source {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/inventory_utils.tcl}
set dst [open {/home/toylog/faeco_tcad_ibex_20261123/hold_repair_sky130_03/original_inventory.txt} w]
set block [ord::get_db_block]
foreach inst [$block getInsts] {
    puts $dst [list instance [$inst getName] [instance_state $inst]]
}
foreach net [$block getNets] {
    if {[$net getSigType] ni {POWER GROUND}} {
        puts $dst [list net [$net getName] [connection_state $net]]
    }
}
close $dst
puts ORIGINAL_INVENTORY_COMPLETE
exit
