module dff(CK,D,Q);
input CK, D;
output Q;
sky130_fd_sc_hd__buf_1 g (.A(D), .X(Q));
endmodule
module top(A,EN,Y,Q);
input A, EN;
output Y, Q;
sky130_fd_sc_hd__einvn_1 g (.A(A), .TE_B(1'b0), .Z(Y));
dff seq (.CK(A), .D(A), .Q(Q));
endmodule
