// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__einvp_1 (A, TE, Z);
  input A, TE;
  output Z;
  assign Z = ((~(TE))) ? 1'bz : ((!A));
endmodule
