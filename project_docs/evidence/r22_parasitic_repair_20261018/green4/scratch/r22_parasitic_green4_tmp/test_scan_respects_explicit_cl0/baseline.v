module top(alternate_clk, a, y);
input alternate_clk;
input a;
output y;
wire n;
sky130_fd_sc_hd__probea_1 u0 (.A(a), .Y(n));
sky130_fd_sc_hd__probea_1 u1 (.A(n), .Y(y));
endmodule
