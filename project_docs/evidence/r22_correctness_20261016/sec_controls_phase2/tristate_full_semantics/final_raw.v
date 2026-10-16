module top(A,TE_B,Z);
input A,TE_B;
output Z;
sky130_fd_sc_hd__einvn_1 g(.A(A),.TE_B(TE_B),.Z(Z));
endmodule
