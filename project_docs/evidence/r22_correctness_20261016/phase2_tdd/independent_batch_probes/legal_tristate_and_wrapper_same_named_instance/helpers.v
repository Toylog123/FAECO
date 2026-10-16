module dff(CK,D,Q);
input CK, D;
output Q;
sky130_fd_sc_hd__buf_1 g (.A(D), .X(Q));
endmodule