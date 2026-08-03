; benchmark generated from python API
(set-info :status unknown)
(declare-fun |assign sign = 1'h1| () Bool)
(declare-fun |\\opcode[1]| () Bool)
(declare-fun |assign n35 = \\opcode[0]| () Bool)
(assert
 (let (($x12 (and |assign n35 = \\opcode[0]| (not |\\opcode[1]|))))
(and (distinct $x12 |assign sign = 1'h1|) true)))
(check-sat)
