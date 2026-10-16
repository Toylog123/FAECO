module top(A,EN,Y,Q);
input A, EN;
output Y, Q;
sky130_fd_sc_hd__einvn_1 g (.A(A), .TE_B(EN), .Z(Y));
dff seq (.CK(A), .D(A), .Q(Q));
endmodule