module top(A,TE,Z);
input A,TE;
output Z;
wire wrong_enable;
assign wrong_enable=~TE;
sky130_fd_sc_hd__einvp_1 g(.A(A),.TE(wrong_enable),.Z(Z));
endmodule