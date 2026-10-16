module top(A,TE,Z);
input A,TE;
output Z;
sky130_fd_sc_hd__einvp_1 g(.A(A),.TE(TE),.Z(Z));
endmodule