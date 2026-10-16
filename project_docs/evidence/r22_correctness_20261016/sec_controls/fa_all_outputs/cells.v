// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__fa_1 (A, B, CIN, COUT, SUM);
  input A, B, CIN;
  output COUT, SUM;
  assign COUT = (A&B) | (A&CIN) | (B&CIN);
  assign SUM = (A&!B&!CIN) | (!A&B&!CIN) | (!A&!B&CIN) | (A&B&CIN);
endmodule
