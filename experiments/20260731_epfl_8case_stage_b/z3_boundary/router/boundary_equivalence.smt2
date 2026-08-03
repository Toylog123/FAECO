; benchmark generated from python API
(set-info :status unknown)
(declare-fun |assign \\outport[10]  = 1'h0| () Bool)
(declare-fun |\\dest_x[10]| () Bool)
(declare-fun |assign n92 = ~\\dest_x[9]| () Bool)
(assert
 (let (($x32 (and |assign n92 = ~\\dest_x[9]| (not |\\dest_x[10]|))))
(and (distinct $x32 |assign \\outport[10]  = 1'h0|) true)))
(check-sat)
