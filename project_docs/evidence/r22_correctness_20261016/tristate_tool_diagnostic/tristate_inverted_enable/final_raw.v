module top(A,TE_B,Z);
input A,TE_B;
output Z;
wire wrong_enable;
assign wrong_enable=~TE_B;
sky130_fd_sc_hd__einvn_1 g(.A(A),.TE_B(wrong_enable),.Z(Z));
endmodule
