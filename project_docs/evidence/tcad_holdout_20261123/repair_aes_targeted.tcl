# Constrain the reused local-route repair pipeline to exactly one residual sink.
set common $::env(FAECO_HOLDOUT_COMMON_TCL)
rename repair_timing faeco_original_repair_timing
proc repair_timing {args} {
    set paths [find_timing_paths -path_delay min -slack_max 0 -group_path_count 20 -endpoint_path_count 1]
    set sinks [dict create]
    foreach path $paths {
        if {[get_property $path slack] >= 0} { continue }
        set pin [get_property $path endpoint]
        dict set sinks [get_full_name $pin] $pin
    }
    set expected {u0.w[1][6]$_DFF_P_/D}
    if {[dict size $sinks] != 1 || ![dict exists $sinks $expected]} {
        error "Unexpected residual negative hold endpoints: [dict keys $sinks]"
    }
    set pin [dict get $sinks $expected]
    set cell sky130_fd_sc_hd__dlygate4sd1_1
    puts "TARGETED_HOLD startpoint=key\[70\] sink=$expected cell=$cell margin_ns=$::env(FAECO_HOLDOUT_MARGIN_NS)"
    set inst [insert_buffer -load_pins [list $pin] -buffer_cell $cell \
        -buffer_name faeco_hold_target_v2 -net_name faeco_hold_target_v2_net]
    if {$inst in {"" "NULL"} || [get_property $inst ref_name] ne $cell} {
        error "Targeted sink delay buffer was not inserted"
    }
    set output [get_full_name $inst]/X
    set sink_pins {}
    foreach connected [get_pins -of_objects [get_nets -of_objects [list $pin]]] {
        lappend sink_pins [get_full_name $connected]
    }
    if {[lsort $sink_pins] ne [lsort [list $output $expected]]} {
        error "Unexpected targeted output net connections: $sink_pins"
    }
    puts "TARGETED_HOLD_VERIFIED buffer=[get_full_name $inst] output=$output sink=$expected"
}
source $common
