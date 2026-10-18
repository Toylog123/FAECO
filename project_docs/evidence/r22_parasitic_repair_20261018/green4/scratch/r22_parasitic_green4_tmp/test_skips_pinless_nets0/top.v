module top(A, Y);
  input A; output Y;
  wire unused;
  wire a2;
  assign a2 = A;
  sky130_fd_sc_hd__buf_1 u1 (.A(a2), .X(Y));
endmodule
