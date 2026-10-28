// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__a21boi_0 (A1, A2, B1_N, Y);
  input A1, A2, B1_N;
  output Y;
  assign Y = (!A1&B1_N) | (!A2&B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_1 (A1, A2, B1_N, Y);
  input A1, A2, B1_N;
  output Y;
  assign Y = (!A1&B1_N) | (!A2&B1_N);
endmodule

module sky130_fd_sc_hd__clkinv_1 (A, Y);
  input A;
  output Y;
  assign Y = (!A);
endmodule

module sky130_fd_sc_hd__dfxtp_1 (CLK, D, Q);
  input CLK, D;
  output Q;
  reg IQ;
  always @(posedge CLK) IQ <= D;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_1 (A, SLEEP, X);
  input A, SLEEP;
  output X;
  assign X = (A&!SLEEP);
endmodule

module sky130_fd_sc_hd__nor2_1 (A, B, Y);
  input A, B;
  output Y;
  assign Y = (!A&!B);
endmodule

module sky130_fd_sc_hd__nor3b_1 (A, B, C_N, Y);
  input A, B, C_N;
  output Y;
  assign Y = (!A&!B&C_N);
endmodule

module sky130_fd_sc_hd__nor3b_2 (A, B, C_N, Y);
  input A, B, C_N;
  output Y;
  assign Y = (!A&!B&C_N);
endmodule

module sky130_fd_sc_hd__o21a_1 (A1, A2, B1, X);
  input A1, A2, B1;
  output X;
  assign X = (A1&B1) | (A2&B1);
endmodule

module sky130_fd_sc_hd__o21ai_0 (A1, A2, B1, Y);
  input A1, A2, B1;
  output Y;
  assign Y = (!A1&!A2) | (!B1);
endmodule
