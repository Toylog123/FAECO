module dff(CK, D, Q);
  input CK; input D; output Q;
  sky130_fd_sc_hd__dfxtp_1 _0_ (.CLK(CK), .D(D), .Q(Q));
endmodule
module top(CK, A, Y);
  input CK; input A; output Y;
  dff f1 (.CK(CK), .D(A), .Q(Y));
endmodule
