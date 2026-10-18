// Generated from Liberty for symmetric Yosys/ABC SEC.

module sky130_fd_sc_hd__a2111oi_0 (A1, A2, B1, C1, D1, Y);
  input A1, A2, B1, C1, D1;
  output Y;
  assign Y = (!A1&!B1&!C1&!D1) | (!A2&!B1&!C1&!D1);
endmodule

module sky130_fd_sc_hd__a2111oi_1 (A1, A2, B1, C1, D1, Y);
  input A1, A2, B1, C1, D1;
  output Y;
  assign Y = (!A1&!B1&!C1&!D1) | (!A2&!B1&!C1&!D1);
endmodule

module sky130_fd_sc_hd__a2111oi_2 (A1, A2, B1, C1, D1, Y);
  input A1, A2, B1, C1, D1;
  output Y;
  assign Y = (!A1&!B1&!C1&!D1) | (!A2&!B1&!C1&!D1);
endmodule

module sky130_fd_sc_hd__a2111oi_4 (A1, A2, B1, C1, D1, Y);
  input A1, A2, B1, C1, D1;
  output Y;
  assign Y = (!A1&!B1&!C1&!D1) | (!A2&!B1&!C1&!D1);
endmodule

module sky130_fd_sc_hd__a211o_1 (A1, A2, B1, C1, X);
  input A1, A2, B1, C1;
  output X;
  assign X = (A1&A2) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a211oi_1 (A1, A2, B1, C1, Y);
  input A1, A2, B1, C1;
  output Y;
  assign Y = (!A1&!B1&!C1) | (!A2&!B1&!C1);
endmodule

module sky130_fd_sc_hd__a21bo_1 (A1, A2, B1_N, X);
  input A1, A2, B1_N;
  output X;
  assign X = (A1&A2) | (!B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_0 (A1, A2, B1_N, Y);
  input A1, A2, B1_N;
  output Y;
  assign Y = (!A1&B1_N) | (!A2&B1_N);
endmodule

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

module sky130_fd_sc_hd__a21oi_2 (A1, A2, B1, Y);
  input A1, A2, B1;
  output Y;
  assign Y = (!A1&!B1) | (!A2&!B1);
endmodule

module sky130_fd_sc_hd__a221oi_1 (A1, A2, B1, B2, C1, Y);
  input A1, A2, B1, B2, C1;
  output Y;
  assign Y = (!A1&!B1&!C1) | (!A1&!B2&!C1) | (!A2&!B1&!C1) | (!A2&!B2&!C1);
endmodule

module sky130_fd_sc_hd__a22o_1 (A1, A2, B1, B2, X);
  input A1, A2, B1, B2;
  output X;
  assign X = (B1&B2) | (A1&A2);
endmodule

module sky130_fd_sc_hd__a22oi_1 (A1, A2, B1, B2, Y);
  input A1, A2, B1, B2;
  output Y;
  assign Y = (!A1&!B1) | (!A1&!B2) | (!A2&!B1) | (!A2&!B2);
endmodule

module sky130_fd_sc_hd__a311oi_1 (A1, A2, A3, B1, C1, Y);
  input A1, A2, A3, B1, C1;
  output Y;
  assign Y = (!A1&!B1&!C1) | (!A2&!B1&!C1) | (!A3&!B1&!C1);
endmodule

module sky130_fd_sc_hd__a31o_1 (A1, A2, A3, B1, X);
  input A1, A2, A3, B1;
  output X;
  assign X = (A1&A2&A3) | (B1);
endmodule

module sky130_fd_sc_hd__a31oi_1 (A1, A2, A3, B1, Y);
  input A1, A2, A3, B1;
  output Y;
  assign Y = (!A1&!B1) | (!A2&!B1) | (!A3&!B1);
endmodule

module sky130_fd_sc_hd__a32oi_1 (A1, A2, A3, B1, B2, Y);
  input A1, A2, A3, B1, B2;
  output Y;
  assign Y = (!A1&!B1) | (!A1&!B2) | (!A2&!B1) | (!A3&!B1) | (!A2&!B2) | (!A3&!B2);
endmodule

module sky130_fd_sc_hd__a41o_1 (A1, A2, A3, A4, B1, X);
  input A1, A2, A3, A4, B1;
  output X;
  assign X = (A1&A2&A3&A4) | (B1);
endmodule

module sky130_fd_sc_hd__a41oi_1 (A1, A2, A3, A4, B1, Y);
  input A1, A2, A3, A4, B1;
  output Y;
  assign Y = (!A1&!B1) | (!A2&!B1) | (!A3&!B1) | (!A4&!B1);
endmodule

module sky130_fd_sc_hd__a41oi_2 (A1, A2, A3, A4, B1, Y);
  input A1, A2, A3, A4, B1;
  output Y;
  assign Y = (!A1&!B1) | (!A2&!B1) | (!A3&!B1) | (!A4&!B1);
endmodule

module sky130_fd_sc_hd__and2_0 (A, B, X);
  input A, B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_1 (A, B, X);
  input A, B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_2 (A, B, X);
  input A, B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_4 (A, B, X);
  input A, B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and3_1 (A, B, C, X);
  input A, B, C;
  output X;
  assign X = (A&B&C);
endmodule

module sky130_fd_sc_hd__and3b_1 (A_N, B, C, X);
  input A_N, B, C;
  output X;
  assign X = (!A_N&B&C);
endmodule

module sky130_fd_sc_hd__and4_1 (A, B, C, D, X);
  input A, B, C, D;
  output X;
  assign X = (A&B&C&D);
endmodule

module sky130_fd_sc_hd__and4_4 (A, B, C, D, X);
  input A, B, C, D;
  output X;
  assign X = (A&B&C&D);
endmodule

module sky130_fd_sc_hd__and4b_1 (A_N, B, C, D, X);
  input A_N, B, C, D;
  output X;
  assign X = (!A_N&B&C&D);
endmodule

module sky130_fd_sc_hd__buf_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkinv_1 (A, Y);
  input A;
  output Y;
  assign Y = (!A);
endmodule

module sky130_fd_sc_hd__clkinv_2 (A, Y);
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

module sky130_fd_sc_hd__einvn_1 (A, TE_B, Z);
  input A, TE_B;
  output Z;
  assign Z = ((TE_B)) ? 1'bz : ((!A));
endmodule

module sky130_fd_sc_hd__einvp_2 (A, TE, Z);
  input A, TE;
  output Z;
  assign Z = ((~(TE))) ? 1'bz : ((!A));
endmodule

module sky130_fd_sc_hd__inv_1 (A, Y);
  input A;
  output Y;
  assign Y = (!A);
endmodule

module sky130_fd_sc_hd__inv_2 (A, Y);
  input A;
  output Y;
  assign Y = (!A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_1 (A, Y);
  input A;
  output Y;
  assign Y = (!A);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso0n_1 (A, SLEEP_B, X);
  input A, SLEEP_B;
  output X;
  assign X = (SLEEP_B&A);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso1n_1 (A, SLEEP_B, X);
  input A, SLEEP_B;
  output X;
  assign X = (A) | (!SLEEP_B);
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

module sky130_fd_sc_hd__mux2i_1 (A0, A1, S, Y);
  input A0, A1, S;
  output Y;
  assign Y = (!A0&!S) | (!A1&S);
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

module sky130_fd_sc_hd__nand4_2 (A, B, C, D, Y);
  input A, B, C, D;
  output Y;
  assign Y = (!A) | (!B) | (!C) | (!D);
endmodule

module sky130_fd_sc_hd__nand4b_1 (A_N, B, C, D, Y);
  input A_N, B, C, D;
  output Y;
  assign Y = (A_N) | (!B) | (!C) | (!D);
endmodule

module sky130_fd_sc_hd__nand4bb_1 (A_N, B_N, C, D, Y);
  input A_N, B_N, C, D;
  output Y;
  assign Y = (A_N) | (B_N) | (!C) | (!D);
endmodule

module sky130_fd_sc_hd__nor2_1 (A, B, Y);
  input A, B;
  output Y;
  assign Y = (!A&!B);
endmodule

module sky130_fd_sc_hd__nor2b_1 (A, B_N, Y);
  input A, B_N;
  output Y;
  assign Y = (!A&B_N);
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

module sky130_fd_sc_hd__nor3b_2 (A, B, C_N, Y);
  input A, B, C_N;
  output Y;
  assign Y = (!A&!B&C_N);
endmodule

module sky130_fd_sc_hd__nor4_1 (A, B, C, D, Y);
  input A, B, C, D;
  output Y;
  assign Y = (!A&!B&!C&!D);
endmodule

module sky130_fd_sc_hd__nor4_2 (A, B, C, D, Y);
  input A, B, C, D;
  output Y;
  assign Y = (!A&!B&!C&!D);
endmodule

module sky130_fd_sc_hd__nor4_4 (A, B, C, D, Y);
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

module sky130_fd_sc_hd__o2111a_1 (A1, A2, B1, C1, D1, X);
  input A1, A2, B1, C1, D1;
  output X;
  assign X = (A1&B1&C1&D1) | (A2&B1&C1&D1);
endmodule

module sky130_fd_sc_hd__o2111ai_1 (A1, A2, B1, C1, D1, Y);
  input A1, A2, B1, C1, D1;
  output Y;
  assign Y = (!A1&!A2) | (!B1) | (!C1) | (!D1);
endmodule

module sky130_fd_sc_hd__o211a_1 (A1, A2, B1, C1, X);
  input A1, A2, B1, C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1);
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

module sky130_fd_sc_hd__o21ai_1 (A1, A2, B1, Y);
  input A1, A2, B1;
  output Y;
  assign Y = (!A1&!A2) | (!B1);
endmodule

module sky130_fd_sc_hd__o21ba_1 (A1, A2, B1_N, X);
  input A1, A2, B1_N;
  output X;
  assign X = (A1&!B1_N) | (A2&!B1_N);
endmodule

module sky130_fd_sc_hd__o21bai_1 (A1, A2, B1_N, Y);
  input A1, A2, B1_N;
  output Y;
  assign Y = (!A1&!A2) | (B1_N);
endmodule

module sky130_fd_sc_hd__o221a_1 (A1, A2, B1, B2, C1, X);
  input A1, A2, B1, B2, C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A1&B2&C1) | (A2&B2&C1);
endmodule

module sky130_fd_sc_hd__o221ai_1 (A1, A2, B1, B2, C1, Y);
  input A1, A2, B1, B2, C1;
  output Y;
  assign Y = (!B1&!B2) | (!A1&!A2) | (!C1);
endmodule

module sky130_fd_sc_hd__o22a_1 (A1, A2, B1, B2, X);
  input A1, A2, B1, B2;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A1&B2) | (A2&B2);
endmodule

module sky130_fd_sc_hd__o22ai_1 (A1, A2, B1, B2, Y);
  input A1, A2, B1, B2;
  output Y;
  assign Y = (!B1&!B2) | (!A1&!A2);
endmodule

module sky130_fd_sc_hd__o311ai_0 (A1, A2, A3, B1, C1, Y);
  input A1, A2, A3, B1, C1;
  output Y;
  assign Y = (!A1&!A2&!A3) | (!B1) | (!C1);
endmodule

module sky130_fd_sc_hd__o31a_1 (A1, A2, A3, B1, X);
  input A1, A2, A3, B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1);
endmodule

module sky130_fd_sc_hd__o31a_4 (A1, A2, A3, B1, X);
  input A1, A2, A3, B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1);
endmodule

module sky130_fd_sc_hd__o31ai_1 (A1, A2, A3, B1, Y);
  input A1, A2, A3, B1;
  output Y;
  assign Y = (!A1&!A2&!A3) | (!B1);
endmodule

module sky130_fd_sc_hd__o32ai_1 (A1, A2, A3, B1, B2, Y);
  input A1, A2, A3, B1, B2;
  output Y;
  assign Y = (!A1&!A2&!A3) | (!B1&!B2);
endmodule

module sky130_fd_sc_hd__o41ai_1 (A1, A2, A3, A4, B1, Y);
  input A1, A2, A3, A4, B1;
  output Y;
  assign Y = (!A1&!A2&!A3&!A4) | (!B1);
endmodule

module sky130_fd_sc_hd__or2b_2 (A, B_N, X);
  input A, B_N;
  output X;
  assign X = (A) | (!B_N);
endmodule

module sky130_fd_sc_hd__or3_1 (A, B, C, X);
  input A, B, C;
  output X;
  assign X = (A) | (B) | (C);
endmodule

module sky130_fd_sc_hd__or3b_1 (A, B, C_N, X);
  input A, B, C_N;
  output X;
  assign X = (A) | (B) | (!C_N);
endmodule

module sky130_fd_sc_hd__or4_1 (A, B, C, D, X);
  input A, B, C, D;
  output X;
  assign X = (A) | (B) | (C) | (D);
endmodule

module sky130_fd_sc_hd__or4b_1 (A, B, C, D_N, X);
  input A, B, C, D_N;
  output X;
  assign X = (A) | (B) | (C) | (!D_N);
endmodule

module sky130_fd_sc_hd__or4b_4 (A, B, C, D_N, X);
  input A, B, C, D_N;
  output X;
  assign X = (A) | (B) | (C) | (!D_N);
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
