module top(CLK,D,DE,Q);
input CLK,D,DE;
output Q;
wire wrong_enable;
assign wrong_enable=~DE;
sky130_fd_sc_hd__edfxtp_1 g(.CLK(CLK),.D(D),.DE(wrong_enable),.Q(Q));
endmodule
