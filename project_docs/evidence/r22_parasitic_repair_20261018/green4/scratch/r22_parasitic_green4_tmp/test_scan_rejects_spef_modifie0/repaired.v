module top(CK, a, y);
input CK;
input a;
output y;
wire n;
sky130_fd_sc_hd__probeb_1 u0 (.A(a), .Z(n));
sky130_fd_sc_hd__probea_1 u1 (.A(n), .Y(y));
endmodule
