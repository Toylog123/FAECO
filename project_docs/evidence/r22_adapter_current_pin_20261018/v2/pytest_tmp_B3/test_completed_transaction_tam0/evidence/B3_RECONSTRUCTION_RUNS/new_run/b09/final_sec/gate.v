module b09(A,Y);
input A;
output Y;
sky130_fd_sc_hd__buf_2 g (.A(A),.X(Y));
endmodule