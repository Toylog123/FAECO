module sky130_fd_sc_hd__a22o_1 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (A1&A2);
endmodule

module sky130_fd_sc_hd__nand2_1 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A) | (~B);
endmodule

module sky130_fd_sc_hd__o21a_1 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1);
endmodule

