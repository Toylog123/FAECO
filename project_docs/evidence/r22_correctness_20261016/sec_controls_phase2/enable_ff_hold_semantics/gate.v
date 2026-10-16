module top(CLK,D,DE,Q);
input CLK,D,DE;
output Q;
sky130_fd_sc_hd__edfxtp_1 g(.CLK(CLK),.D(D),.DE(DE),.Q(Q));
endmodule