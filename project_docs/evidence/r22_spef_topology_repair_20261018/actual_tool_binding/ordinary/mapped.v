module top(input CK,A,output Z); wire qvec, qlit;
sky130_fd_sc_hd__dfxtp_1 f0 (.CLK(CK),.D(A),.Q(qvec));
sky130_fd_sc_hd__buf_1 b0 (.A(qvec),.X(qlit));
sky130_fd_sc_hd__dfxtp_1 f1 (.CLK(CK),.D(qlit),.Q(Z));
endmodule
