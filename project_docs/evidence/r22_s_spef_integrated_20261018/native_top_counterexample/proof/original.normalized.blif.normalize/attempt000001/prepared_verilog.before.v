module ztop(input A,B,output Y); wire n;
sky130_fd_sc_hd__buf_1 g1 (.A(A),.X(Y));
sky130_fd_sc_hd__buf_1 g2 (.A(B),.X(n)); endmodule
