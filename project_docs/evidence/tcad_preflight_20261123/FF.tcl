read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_AO_RVT_FF_nldm_211120.lib.gz}
read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_INVBUF_RVT_FF_nldm_220122.lib.gz}
read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_OA_RVT_FF_nldm_211120.lib.gz}
read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_SIMPLE_RVT_FF_nldm_211120.lib.gz}
read_liberty {/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_SEQ_RVT_FF_nldm_220123.lib}
read_verilog {/home/toylog/rseco_timing/adaptive_20261120/rcx_smoke/results/asap7/gcd/base/6_final.v}
link_design gcd
read_sdc {/home/toylog/rseco_timing/adaptive_20261120/rcx_smoke/results/asap7/gcd/base/6_final.sdc}
read_spef {/home/toylog/rseco_timing/adaptive_20261120/rcx_smoke/results/asap7/gcd/base/6_final.spef}
puts "GCD_SETUP_SECONDS [sta::worst_slack_cmd max]"
puts "GCD_HOLD_SECONDS [sta::worst_slack_cmd min]"
report_units
check_setup -verbose
report_check_types -max_slew -max_capacitance -violators
report_checks -path_delay min -format full_clock_expanded -digits 6
puts "PREFLIGHT_STA_COMPLETE"
exit
