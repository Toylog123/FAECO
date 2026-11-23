set root /home/toylog/faeco_tcad_ibex_20261123
set source $root/control_sky130/results/sky130hd/ibex/base/6_final
set out $root/hold_repair_sky130_dry_root
set flow /home/toylog/faeco_eda/orfs/flow
set extra /home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd
define_corners TT FF SS
read_liberty -corner TT $flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty -corner FF $extra/sky130_fd_sc_hd__ff_n40C_1v95.lib
read_liberty -corner SS $extra/sky130_fd_sc_hd__ss_n40C_1v40.lib
read_db $source.odb
read_sdc $source.sdc
foreach corner {TT FF SS} { read_spef -corner $corner $source.spef }
source $flow/platforms/sky130hd/setRC.tcl
puts "DRY_BEFORE_HOLD_SECONDS [sta::worst_slack_cmd min]"
puts "DRY_BEFORE_SETUP_SECONDS [sta::worst_slack_cmd max]"
report_checks -path_delay min -group_path_count 4 -digits 6
report_design_area
repair_timing -hold -hold_margin 0.05 -max_buffer_percent 10 -allow_setup_violations
puts "DRY_AFTER_HOLD_SECONDS [sta::worst_slack_cmd min]"
puts "DRY_AFTER_SETUP_SECONDS [sta::worst_slack_cmd max]"
report_checks -path_delay min -group_path_count 4 -digits 6
report_design_area
write_db $out/dry.odb
puts DRY_REPAIR_COMPLETE
exit
