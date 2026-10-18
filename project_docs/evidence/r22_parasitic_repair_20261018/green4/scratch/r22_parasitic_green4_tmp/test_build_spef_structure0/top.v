module top(CK, A, Y);
  input CK; input A; output Y;
  sky130_fd_sc_hd__buf_1 u1 (.A(A), .X(n1));
  sky130_fd_sc_hd__inv_1 u2 (.A(n1), .Y(Y));
  sky130_fd_sc_hd__dfxtp_1 u3 (.CLK(CK), .D(n1), .Q(q1));
endmodule
