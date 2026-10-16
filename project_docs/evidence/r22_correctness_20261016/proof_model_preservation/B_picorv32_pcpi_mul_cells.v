// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__a21o_1 (A1, A2, B1, X);
  input A1, A2, B1;
  output X;
  assign X = (A1&A2) | (B1);
endmodule

module sky130_fd_sc_hd__a21oi_1 (A1, A2, B1, Y);
  input A1, A2, B1;
  output Y;
  assign Y = (!A1&!B1) | (!A2&!B1);
endmodule

module sky130_fd_sc_hd__a31o_1 (A1, A2, A3, B1, X);
  input A1, A2, A3, B1;
  output X;
  assign X = (A1&A2&A3) | (B1);
endmodule

module sky130_fd_sc_hd__and2_0 (A, B, X);
  input A, B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and3_1 (A, B, C, X);
  input A, B, C;
  output X;
  assign X = (A&B&C);
endmodule

module sky130_fd_sc_hd__buf_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkbuf_1 (A, X);
  input A;
  output X;
  assign X = (A);
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

module sky130_fd_sc_hd__edfxtp_1 (CLK, D, DE, Q);
  input CLK, D, DE;
  output Q;
  reg IQ;
  always @(posedge CLK) IQ <= (D&DE) | (IQ&!DE);
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__lpflow_inputiso1p_1 (A, SLEEP, X);
  input A, SLEEP;
  output X;
  assign X = (A) | (SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_1 (A, SLEEP, X);
  input A, SLEEP;
  output X;
  assign X = (A&!SLEEP);
endmodule

module sky130_fd_sc_hd__mux2_1 (A0, A1, S, X);
  input A0, A1, S;
  output X;
  assign X = (A0&!S) | (A1&S);
endmodule

module sky130_fd_sc_hd__nand2_1 (A, B, Y);
  input A, B;
  output Y;
  assign Y = (!A) | (!B);
endmodule

module sky130_fd_sc_hd__nand2b_1 (A_N, B, Y);
  input A_N, B;
  output Y;
  assign Y = (A_N) | (!B);
endmodule

module sky130_fd_sc_hd__nand3_1 (A, B, C, Y);
  input A, B, C;
  output Y;
  assign Y = (!A) | (!B) | (!C);
endmodule

module sky130_fd_sc_hd__nand3_4 (A, B, C, Y);
  input A, B, C;
  output Y;
  assign Y = (!A) | (!B) | (!C);
endmodule

module sky130_fd_sc_hd__nand3b_1 (A_N, B, C, Y);
  input A_N, B, C;
  output Y;
  assign Y = (A_N) | (!B) | (!C);
endmodule

module sky130_fd_sc_hd__nand4_1 (A, B, C, D, Y);
  input A, B, C, D;
  output Y;
  assign Y = (!A) | (!B) | (!C) | (!D);
endmodule

module sky130_fd_sc_hd__nand4b_1 (A_N, B, C, D, Y);
  input A_N, B, C, D;
  output Y;
  assign Y = (A_N) | (!B) | (!C) | (!D);
endmodule

module sky130_fd_sc_hd__nor2_1 (A, B, Y);
  input A, B;
  output Y;
  assign Y = (!A&!B);
endmodule

module sky130_fd_sc_hd__nor3_1 (A, B, C, Y);
  input A, B, C;
  output Y;
  assign Y = (!A&!B&!C);
endmodule

module sky130_fd_sc_hd__nor3b_1 (A, B, C_N, Y);
  input A, B, C_N;
  output Y;
  assign Y = (!A&!B&C_N);
endmodule

module sky130_fd_sc_hd__nor4_1 (A, B, C, D, Y);
  input A, B, C, D;
  output Y;
  assign Y = (!A&!B&!C&!D);
endmodule

module sky130_fd_sc_hd__nor4b_1 (A, B, C, D_N, Y);
  input A, B, C, D_N;
  output Y;
  assign Y = (!A&!B&!C&D_N);
endmodule

module sky130_fd_sc_hd__nor4bb_1 (A, B, C_N, D_N, Y);
  input A, B, C_N, D_N;
  output Y;
  assign Y = (!A&!B&C_N&D_N);
endmodule

module sky130_fd_sc_hd__o211ai_1 (A1, A2, B1, C1, Y);
  input A1, A2, B1, C1;
  output Y;
  assign Y = (!A1&!A2) | (!B1) | (!C1);
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

module sky130_fd_sc_hd__o21bai_1 (A1, A2, B1_N, Y);
  input A1, A2, B1_N;
  output Y;
  assign Y = (!A1&!A2) | (B1_N);
endmodule

module sky130_fd_sc_hd__xnor2_1 (A, B, Y);
  input A, B;
  output Y;
  assign Y = (!A&!B) | (A&B);
endmodule

module sky130_fd_sc_hd__xor2_1 (A, B, X);
  input A, B;
  output X;
  assign X = (A&!B) | (!A&B);
endmodule
