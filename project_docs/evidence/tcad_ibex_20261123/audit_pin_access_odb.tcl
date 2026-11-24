# Describe OpenDB pin-access geometry and serialize a copy without access points.
# The input is read-only. These outputs are for diagnosis, not routing.
set input [file normalize $::env(FAECO_PA_AUDIT_INPUT)]
set output [file normalize $::env(FAECO_PA_AUDIT_OUTPUT)]
if {$input eq $output || [file exists $output]} {
    error "Use a fresh diagnostic output distinct from the input"
}

read_db $input
set block [ord::get_db_block]
set points {}
set ids {}
foreach ap [$block getAccessPoints] {
    set point [$ap getPoint]
    set loc [concat $point [list [[$ap getLayer] getName]]]
    set term [$ap getMPin]
    if {$term ne "NULL"} {
        set owner [list master [[$term getMaster] getName] [[$term getMTerm] getName]]
    } else {
        set owner [list block [[[$ap getBPin] getBTerm] getName]]
    }
    lappend points [concat $owner $loc [list [$ap getLowType] [$ap getHighType]]]
    lappend ids [$ap getId]
}

foreach row [lsort $points] {
    puts "FAECO_PA_POINT $row"
}
puts "FAECO_PA_COUNT [llength $ids]"

foreach id [lsort -integer $ids] {
    odb::dbAccessPoint_destroy [odb::dbAccessPoint_getAccessPoint $block $id]
}
if {[llength [$block getAccessPoints]] != 0} {
    error "Pin-access points remain after diagnostic normalization"
}
write_db $output
puts FAECO_PA_AUDIT_COMPLETE
exit
