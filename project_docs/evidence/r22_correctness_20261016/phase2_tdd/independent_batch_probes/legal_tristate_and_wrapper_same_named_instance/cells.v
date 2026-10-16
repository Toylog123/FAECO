// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__buf_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__einvn_1 (A, TE_B, Z);
  input A, TE_B;
  output Z;
  assign Z = ((TE_B)) ? 1'bz : ((!A));
endmodule
