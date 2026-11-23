proc instance_state {inst} {
    return [list [$inst getLocation] [$inst getOrient] [[$inst getMaster] getName]]
}
proc connection_state {net} {
    set pins {}
    foreach pin [$net getITerms] {
        lappend pins [list [[$pin getInst] getName] [[$pin getMTerm] getName]]
    }
    foreach pin [$net getBTerms] {
        lappend pins [list PORT [$pin getName]]
    }
    return [lsort -ascii $pins]
}
