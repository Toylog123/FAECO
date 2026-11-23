read_liberty {/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd/sky130_fd_sc_hd__ss_n40C_1v40.lib}
read_db {/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/6_final.odb}
read_sdc {/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/6_final.sdc}
read_spef {/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/6_final.spef}
set pin [get_pins -regexp {^u0[.]w\[1\]\[6\]\$_DFF_P_/D$}]
if {[llength $pin] != 1} { error "missing exact target D pin" }
set p [lindex [find_timing_paths -path_delay min -to $pin] 0]
puts "TARGET_SS_SLACK_NS [get_property $p slack]"
puts "TARGET_SS_SINK [get_full_name [get_property $p endpoint]]"
puts "EMBEDDED_ROUTES [grt::have_routes]"
puts "DETAILED_ROUTED [design_is_routed]"
exit
