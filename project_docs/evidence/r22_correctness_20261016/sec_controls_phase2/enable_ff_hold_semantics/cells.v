// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__edfxtp_1 (CLK, D, DE, Q);
  input CLK, D, DE;
  output Q;
  reg IQ;
  always @(posedge CLK) IQ <= (D&DE) | (IQ&!DE);
  assign Q = IQ;
endmodule
