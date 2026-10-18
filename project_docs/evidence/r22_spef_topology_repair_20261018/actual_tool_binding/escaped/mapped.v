module top(input CK,A,output Z); wire [0:0] q; wire \q[0] ;
sky130_fd_sc_hd__dfxtp_1 f0 (.CLK(CK),.D(A),.Q(q[0]));
sky130_fd_sc_hd__buf_1 b0 (.A(q[0]),.X(\q[0] ));
sky130_fd_sc_hd__dfxtp_1 f1 (.CLK(CK),.D(\q[0] ),.Q(Z));
endmodule
