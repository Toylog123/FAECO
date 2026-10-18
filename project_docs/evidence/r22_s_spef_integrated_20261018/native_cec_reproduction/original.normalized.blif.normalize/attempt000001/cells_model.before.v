module sky130_fd_sc_hd__a2111o_1 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&A2) | (B1) | (C1) | (D1);
endmodule

module sky130_fd_sc_hd__a2111o_2 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&A2) | (B1) | (C1) | (D1);
endmodule

module sky130_fd_sc_hd__a2111o_4 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&A2) | (B1) | (C1) | (D1);
endmodule

module sky130_fd_sc_hd__a2111oi_0 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~B1&~C1&~D1) | (~A2&~B1&~C1&~D1);
endmodule

module sky130_fd_sc_hd__a2111oi_1 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~B1&~C1&~D1) | (~A2&~B1&~C1&~D1);
endmodule

module sky130_fd_sc_hd__a2111oi_2 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~B1&~C1&~D1) | (~A2&~B1&~C1&~D1);
endmodule

module sky130_fd_sc_hd__a2111oi_4 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~B1&~C1&~D1) | (~A2&~B1&~C1&~D1);
endmodule

module sky130_fd_sc_hd__a211o_1 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a211o_2 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a211o_4 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a211oi_1 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a211oi_2 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a211oi_4 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a21bo_1 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&A2) | (~B1_N);
endmodule

module sky130_fd_sc_hd__a21bo_2 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&A2) | (~B1_N);
endmodule

module sky130_fd_sc_hd__a21bo_4 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&A2) | (~B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_0 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&B1_N) | (~A2&B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_1 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&B1_N) | (~A2&B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_2 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&B1_N) | (~A2&B1_N);
endmodule

module sky130_fd_sc_hd__a21boi_4 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&B1_N) | (~A2&B1_N);
endmodule

module sky130_fd_sc_hd__a21o_1 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&A2) | (B1);
endmodule

module sky130_fd_sc_hd__a21o_2 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&A2) | (B1);
endmodule

module sky130_fd_sc_hd__a21o_4 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&A2) | (B1);
endmodule

module sky130_fd_sc_hd__a21oi_1 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1);
endmodule

module sky130_fd_sc_hd__a21oi_2 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1);
endmodule

module sky130_fd_sc_hd__a21oi_4 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1);
endmodule

module sky130_fd_sc_hd__a221o_1 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (B1&B2) | (A1&A2) | (C1);
endmodule

module sky130_fd_sc_hd__a221o_2 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (B1&B2) | (A1&A2) | (C1);
endmodule

module sky130_fd_sc_hd__a221o_4 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (B1&B2) | (A1&A2) | (C1);
endmodule

module sky130_fd_sc_hd__a221oi_1 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A1&~B2&~C1) | (~A2&~B1&~C1) | (~A2&~B2&~C1);
endmodule

module sky130_fd_sc_hd__a221oi_2 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A1&~B2&~C1) | (~A2&~B1&~C1) | (~A2&~B2&~C1);
endmodule

module sky130_fd_sc_hd__a221oi_4 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A1&~B2&~C1) | (~A2&~B1&~C1) | (~A2&~B2&~C1);
endmodule

module sky130_fd_sc_hd__a222oi_1 (A1, A2, B1, B2, C1, C2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  input C2;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A1&~B1&~C2) | (~A1&~B2&~C1) | (~A2&~B1&~C1) | (~A1&~B2&~C2) | (~A2&~B1&~C2) | (~A2&~B2&~C1) | (~A2&~B2&~C2);
endmodule

module sky130_fd_sc_hd__a22o_1 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (A1&A2);
endmodule

module sky130_fd_sc_hd__a22o_2 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (A1&A2);
endmodule

module sky130_fd_sc_hd__a22o_4 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (A1&A2);
endmodule

module sky130_fd_sc_hd__a22oi_1 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A2&~B2);
endmodule

module sky130_fd_sc_hd__a22oi_2 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A2&~B2);
endmodule

module sky130_fd_sc_hd__a22oi_4 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A2&~B2);
endmodule

module sky130_fd_sc_hd__a2bb2o_1 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (~A1_N&~A2_N);
endmodule

module sky130_fd_sc_hd__a2bb2o_2 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (~A1_N&~A2_N);
endmodule

module sky130_fd_sc_hd__a2bb2o_4 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (B1&B2) | (~A1_N&~A2_N);
endmodule

module sky130_fd_sc_hd__a2bb2oi_1 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (A1_N&~B1) | (A1_N&~B2) | (A2_N&~B1) | (A2_N&~B2);
endmodule

module sky130_fd_sc_hd__a2bb2oi_2 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (A1_N&~B1) | (A1_N&~B2) | (A2_N&~B1) | (A2_N&~B2);
endmodule

module sky130_fd_sc_hd__a2bb2oi_4 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (A1_N&~B1) | (A1_N&~B2) | (A2_N&~B1) | (A2_N&~B2);
endmodule

module sky130_fd_sc_hd__a311o_1 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2&A3) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a311o_2 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2&A3) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a311o_4 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&A2&A3) | (B1) | (C1);
endmodule

module sky130_fd_sc_hd__a311oi_1 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1) | (~A3&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a311oi_2 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1) | (~A3&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a311oi_4 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~B1&~C1) | (~A2&~B1&~C1) | (~A3&~B1&~C1);
endmodule

module sky130_fd_sc_hd__a31o_1 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&A2&A3) | (B1);
endmodule

module sky130_fd_sc_hd__a31o_2 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&A2&A3) | (B1);
endmodule

module sky130_fd_sc_hd__a31o_4 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&A2&A3) | (B1);
endmodule

module sky130_fd_sc_hd__a31oi_1 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1);
endmodule

module sky130_fd_sc_hd__a31oi_2 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1);
endmodule

module sky130_fd_sc_hd__a31oi_4 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1);
endmodule

module sky130_fd_sc_hd__a32o_1 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&A2&A3) | (B1&B2);
endmodule

module sky130_fd_sc_hd__a32o_2 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&A2&A3) | (B1&B2);
endmodule

module sky130_fd_sc_hd__a32o_4 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&A2&A3) | (B1&B2);
endmodule

module sky130_fd_sc_hd__a32oi_1 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A3&~B1) | (~A2&~B2) | (~A3&~B2);
endmodule

module sky130_fd_sc_hd__a32oi_2 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A3&~B1) | (~A2&~B2) | (~A3&~B2);
endmodule

module sky130_fd_sc_hd__a32oi_4 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~B1) | (~A1&~B2) | (~A2&~B1) | (~A3&~B1) | (~A2&~B2) | (~A3&~B2);
endmodule

module sky130_fd_sc_hd__a41o_1 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&A2&A3&A4) | (B1);
endmodule

module sky130_fd_sc_hd__a41o_2 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&A2&A3&A4) | (B1);
endmodule

module sky130_fd_sc_hd__a41o_4 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&A2&A3&A4) | (B1);
endmodule

module sky130_fd_sc_hd__a41oi_1 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1) | (~A4&~B1);
endmodule

module sky130_fd_sc_hd__a41oi_2 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1) | (~A4&~B1);
endmodule

module sky130_fd_sc_hd__a41oi_4 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~B1) | (~A2&~B1) | (~A3&~B1) | (~A4&~B1);
endmodule

module sky130_fd_sc_hd__and2_0 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_1 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_2 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2_4 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&B);
endmodule

module sky130_fd_sc_hd__and2b_1 (A_N, B, X);
  input A_N;
  input B;
  output X;
  assign X = (~A_N&B);
endmodule

module sky130_fd_sc_hd__and2b_2 (A_N, B, X);
  input A_N;
  input B;
  output X;
  assign X = (~A_N&B);
endmodule

module sky130_fd_sc_hd__and2b_4 (A_N, B, X);
  input A_N;
  input B;
  output X;
  assign X = (~A_N&B);
endmodule

module sky130_fd_sc_hd__and3_1 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B&C);
endmodule

module sky130_fd_sc_hd__and3_2 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B&C);
endmodule

module sky130_fd_sc_hd__and3_4 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B&C);
endmodule

module sky130_fd_sc_hd__and3b_1 (A_N, B, C, X);
  input A_N;
  input B;
  input C;
  output X;
  assign X = (~A_N&B&C);
endmodule

module sky130_fd_sc_hd__and3b_2 (A_N, B, C, X);
  input A_N;
  input B;
  input C;
  output X;
  assign X = (~A_N&B&C);
endmodule

module sky130_fd_sc_hd__and3b_4 (A_N, B, C, X);
  input A_N;
  input B;
  input C;
  output X;
  assign X = (~A_N&B&C);
endmodule

module sky130_fd_sc_hd__and4_1 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A&B&C&D);
endmodule

module sky130_fd_sc_hd__and4_2 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A&B&C&D);
endmodule

module sky130_fd_sc_hd__and4_4 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A&B&C&D);
endmodule

module sky130_fd_sc_hd__and4b_1 (A_N, B, C, D, X);
  input A_N;
  input B;
  input C;
  input D;
  output X;
  assign X = (~A_N&B&C&D);
endmodule

module sky130_fd_sc_hd__and4b_2 (A_N, B, C, D, X);
  input A_N;
  input B;
  input C;
  input D;
  output X;
  assign X = (~A_N&B&C&D);
endmodule

module sky130_fd_sc_hd__and4b_4 (A_N, B, C, D, X);
  input A_N;
  input B;
  input C;
  input D;
  output X;
  assign X = (~A_N&B&C&D);
endmodule

module sky130_fd_sc_hd__and4bb_1 (A_N, B_N, C, D, X);
  input A_N;
  input B_N;
  input C;
  input D;
  output X;
  assign X = (~A_N&~B_N&C&D);
endmodule

module sky130_fd_sc_hd__and4bb_2 (A_N, B_N, C, D, X);
  input A_N;
  input B_N;
  input C;
  input D;
  output X;
  assign X = (~A_N&~B_N&C&D);
endmodule

module sky130_fd_sc_hd__and4bb_4 (A_N, B_N, C, D, X);
  input A_N;
  input B_N;
  input C;
  input D;
  output X;
  assign X = (~A_N&~B_N&C&D);
endmodule

module sky130_fd_sc_hd__buf_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_12 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_16 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_6 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__buf_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__bufbuf_16 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__bufbuf_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__bufinv_16 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__bufinv_8 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkbuf_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkbuf_16 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkbuf_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkbuf_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkbuf_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s15_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s15_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s18_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s18_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s25_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s25_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s50_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkdlybuf4s50_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__clkinv_1 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinv_16 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinv_2 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinv_4 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinv_8 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinvlp_2 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__clkinvlp_4 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__dfrtn_1 (CLK_N, D, RESET_B, Q);
  input CLK_N;
  input D;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfrtp_1 (CLK, D, RESET_B, Q);
  input CLK;
  input D;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfrtp_2 (CLK, D, RESET_B, Q);
  input CLK;
  input D;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfrtp_4 (CLK, D, RESET_B, Q);
  input CLK;
  input D;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfstp_1 (CLK, D, SET_B, Q);
  input CLK;
  input D;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfstp_2 (CLK, D, SET_B, Q);
  input CLK;
  input D;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfstp_4 (CLK, D, SET_B, Q);
  input CLK;
  input D;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfxtp_1 (CLK, D, Q);
  input CLK;
  input D;
  output reg Q;
  always @(posedge CLK)
    Q <= D;
endmodule

module sky130_fd_sc_hd__dfxtp_2 (CLK, D, Q);
  input CLK;
  input D;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dfxtp_4 (CLK, D, Q);
  input CLK;
  input D;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlclkp_1 (CLK, GATE, GCLK);
  input CLK;
  input GATE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__dlclkp_2 (CLK, GATE, GCLK);
  input CLK;
  input GATE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__dlclkp_4 (CLK, GATE, GCLK);
  input CLK;
  input GATE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__dlrtn_1 (D, GATE_N, RESET_B, Q);
  input D;
  input GATE_N;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlrtn_2 (D, GATE_N, RESET_B, Q);
  input D;
  input GATE_N;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlrtn_4 (D, GATE_N, RESET_B, Q);
  input D;
  input GATE_N;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlrtp_1 (D, GATE, RESET_B, Q);
  input D;
  input GATE;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlrtp_2 (D, GATE, RESET_B, Q);
  input D;
  input GATE;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlrtp_4 (D, GATE, RESET_B, Q);
  input D;
  input GATE;
  input RESET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlxtn_1 (D, GATE_N, Q);
  input D;
  input GATE_N;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlxtn_2 (D, GATE_N, Q);
  input D;
  input GATE_N;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlxtn_4 (D, GATE_N, Q);
  input D;
  input GATE_N;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlxtp_1 (D, GATE, Q);
  input D;
  input GATE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__dlygate4sd1_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__dlygate4sd2_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__dlygate4sd3_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__dlymetal6s2s_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__dlymetal6s4s_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__dlymetal6s6s_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__ebufn_1 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (A);
endmodule

module sky130_fd_sc_hd__ebufn_2 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (A);
endmodule

module sky130_fd_sc_hd__ebufn_4 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (A);
endmodule

module sky130_fd_sc_hd__ebufn_8 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (A);
endmodule

module sky130_fd_sc_hd__edfxtp_1 (CLK, D, DE, Q);
  input CLK;
  input D;
  input DE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__einvn_0 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvn_1 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvn_2 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvn_4 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvn_8 (A, TE_B, Z);
  input A;
  input TE_B;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvp_1 (A, TE, Z);
  input A;
  input TE;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvp_2 (A, TE, Z);
  input A;
  input TE;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvp_4 (A, TE, Z);
  input A;
  input TE;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__einvp_8 (A, TE, Z);
  input A;
  input TE;
  output Z;
  assign Z = (~A);
endmodule

module sky130_fd_sc_hd__inv_1 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_12 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_16 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_2 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_4 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_6 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__inv_8 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_clkbufkapwr_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_clkbufkapwr_16 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_clkbufkapwr_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_clkbufkapwr_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_clkbufkapwr_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_1 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_16 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_2 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_4 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_clkinvkapwr_8 (A, Y);
  input A;
  output Y;
  assign Y = (~A);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso0n_1 (A, SLEEP_B, X);
  input A;
  input SLEEP_B;
  output X;
  assign X = (SLEEP_B&A);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso0p_1 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (~SLEEP&A);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso1n_1 (A, SLEEP_B, X);
  input A;
  input SLEEP_B;
  output X;
  assign X = (A) | (~SLEEP_B);
endmodule

module sky130_fd_sc_hd__lpflow_inputiso1p_1 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A) | (SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_inputisolatch_1 (D, SLEEP_B, Q);
  input D;
  input SLEEP_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_1 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_16 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_2 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_4 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrc_8 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_isobufsrckapwr_16 (A, SLEEP, X);
  input A;
  input SLEEP;
  output X;
  assign X = (A&~SLEEP);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__maj3_1 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B) | (A&C) | (B&C);
endmodule

module sky130_fd_sc_hd__maj3_2 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B) | (A&C) | (B&C);
endmodule

module sky130_fd_sc_hd__maj3_4 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&B) | (A&C) | (B&C);
endmodule

module sky130_fd_sc_hd__mux2_1 (A0, A1, S, X);
  input A0;
  input A1;
  input S;
  output X;
  assign X = (A0&~S) | (A1&S);
endmodule

module sky130_fd_sc_hd__mux2_2 (A0, A1, S, X);
  input A0;
  input A1;
  input S;
  output X;
  assign X = (A0&~S) | (A1&S);
endmodule

module sky130_fd_sc_hd__mux2_4 (A0, A1, S, X);
  input A0;
  input A1;
  input S;
  output X;
  assign X = (A0&~S) | (A1&S);
endmodule

module sky130_fd_sc_hd__mux2_8 (A0, A1, S, X);
  input A0;
  input A1;
  input S;
  output X;
  assign X = (A0&~S) | (A1&S);
endmodule

module sky130_fd_sc_hd__mux2i_1 (A0, A1, S, Y);
  input A0;
  input A1;
  input S;
  output Y;
  assign Y = (~A0&~S) | (~A1&S);
endmodule

module sky130_fd_sc_hd__mux2i_2 (A0, A1, S, Y);
  input A0;
  input A1;
  input S;
  output Y;
  assign Y = (~A0&~S) | (~A1&S);
endmodule

module sky130_fd_sc_hd__mux2i_4 (A0, A1, S, Y);
  input A0;
  input A1;
  input S;
  output Y;
  assign Y = (~A0&~S) | (~A1&S);
endmodule

module sky130_fd_sc_hd__mux4_1 (A0, A1, A2, A3, S0, S1, X);
  input A0;
  input A1;
  input A2;
  input A3;
  input S0;
  input S1;
  output X;
  assign X = (A0&~S0&~S1) | (A1&S0&~S1) | (A2&~S0&S1) | (A3&S0&S1);
endmodule

module sky130_fd_sc_hd__mux4_2 (A0, A1, A2, A3, S0, S1, X);
  input A0;
  input A1;
  input A2;
  input A3;
  input S0;
  input S1;
  output X;
  assign X = (A0&~S0&~S1) | (A1&S0&~S1) | (A2&~S0&S1) | (A3&S0&S1);
endmodule

module sky130_fd_sc_hd__mux4_4 (A0, A1, A2, A3, S0, S1, X);
  input A0;
  input A1;
  input A2;
  input A3;
  input S0;
  input S1;
  output X;
  assign X = (A0&~S0&~S1) | (A1&S0&~S1) | (A2&~S0&S1) | (A3&S0&S1);
endmodule

module sky130_fd_sc_hd__nand2_1 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A) | (~B);
endmodule

module sky130_fd_sc_hd__nand2_2 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A) | (~B);
endmodule

module sky130_fd_sc_hd__nand2_4 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A) | (~B);
endmodule

module sky130_fd_sc_hd__nand2_8 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A) | (~B);
endmodule

module sky130_fd_sc_hd__nand2b_1 (A_N, B, Y);
  input A_N;
  input B;
  output Y;
  assign Y = (A_N) | (~B);
endmodule

module sky130_fd_sc_hd__nand2b_2 (A_N, B, Y);
  input A_N;
  input B;
  output Y;
  assign Y = (A_N) | (~B);
endmodule

module sky130_fd_sc_hd__nand2b_4 (A_N, B, Y);
  input A_N;
  input B;
  output Y;
  assign Y = (A_N) | (~B);
endmodule

module sky130_fd_sc_hd__nand3_1 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand3_2 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand3_4 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand3b_1 (A_N, B, C, Y);
  input A_N;
  input B;
  input C;
  output Y;
  assign Y = (A_N) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand3b_2 (A_N, B, C, Y);
  input A_N;
  input B;
  input C;
  output Y;
  assign Y = (A_N) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand3b_4 (A_N, B, C, Y);
  input A_N;
  input B;
  input C;
  output Y;
  assign Y = (A_N) | (~B) | (~C);
endmodule

module sky130_fd_sc_hd__nand4_1 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4_2 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4_4 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4b_1 (A_N, B, C, D, Y);
  input A_N;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4b_2 (A_N, B, C, D, Y);
  input A_N;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4b_4 (A_N, B, C, D, Y);
  input A_N;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (~B) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4bb_1 (A_N, B_N, C, D, Y);
  input A_N;
  input B_N;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (B_N) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4bb_2 (A_N, B_N, C, D, Y);
  input A_N;
  input B_N;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (B_N) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nand4bb_4 (A_N, B_N, C, D, Y);
  input A_N;
  input B_N;
  input C;
  input D;
  output Y;
  assign Y = (A_N) | (B_N) | (~C) | (~D);
endmodule

module sky130_fd_sc_hd__nor2_1 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B);
endmodule

module sky130_fd_sc_hd__nor2_2 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B);
endmodule

module sky130_fd_sc_hd__nor2_4 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B);
endmodule

module sky130_fd_sc_hd__nor2_8 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B);
endmodule

module sky130_fd_sc_hd__nor2b_1 (A, B_N, Y);
  input A;
  input B_N;
  output Y;
  assign Y = (~A&B_N);
endmodule

module sky130_fd_sc_hd__nor2b_2 (A, B_N, Y);
  input A;
  input B_N;
  output Y;
  assign Y = (~A&B_N);
endmodule

module sky130_fd_sc_hd__nor2b_4 (A, B_N, Y);
  input A;
  input B_N;
  output Y;
  assign Y = (~A&B_N);
endmodule

module sky130_fd_sc_hd__nor3_1 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A&~B&~C);
endmodule

module sky130_fd_sc_hd__nor3_2 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A&~B&~C);
endmodule

module sky130_fd_sc_hd__nor3_4 (A, B, C, Y);
  input A;
  input B;
  input C;
  output Y;
  assign Y = (~A&~B&~C);
endmodule

module sky130_fd_sc_hd__nor3b_1 (A, B, C_N, Y);
  input A;
  input B;
  input C_N;
  output Y;
  assign Y = (~A&~B&C_N);
endmodule

module sky130_fd_sc_hd__nor3b_2 (A, B, C_N, Y);
  input A;
  input B;
  input C_N;
  output Y;
  assign Y = (~A&~B&C_N);
endmodule

module sky130_fd_sc_hd__nor3b_4 (A, B, C_N, Y);
  input A;
  input B;
  input C_N;
  output Y;
  assign Y = (~A&~B&C_N);
endmodule

module sky130_fd_sc_hd__nor4_1 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A&~B&~C&~D);
endmodule

module sky130_fd_sc_hd__nor4_2 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A&~B&~C&~D);
endmodule

module sky130_fd_sc_hd__nor4_4 (A, B, C, D, Y);
  input A;
  input B;
  input C;
  input D;
  output Y;
  assign Y = (~A&~B&~C&~D);
endmodule

module sky130_fd_sc_hd__nor4b_1 (A, B, C, D_N, Y);
  input A;
  input B;
  input C;
  input D_N;
  output Y;
  assign Y = (~A&~B&~C&D_N);
endmodule

module sky130_fd_sc_hd__nor4b_2 (A, B, C, D_N, Y);
  input A;
  input B;
  input C;
  input D_N;
  output Y;
  assign Y = (~A&~B&~C&D_N);
endmodule

module sky130_fd_sc_hd__nor4b_4 (A, B, C, D_N, Y);
  input A;
  input B;
  input C;
  input D_N;
  output Y;
  assign Y = (~A&~B&~C&D_N);
endmodule

module sky130_fd_sc_hd__nor4bb_1 (A, B, C_N, D_N, Y);
  input A;
  input B;
  input C_N;
  input D_N;
  output Y;
  assign Y = (~A&~B&C_N&D_N);
endmodule

module sky130_fd_sc_hd__nor4bb_2 (A, B, C_N, D_N, Y);
  input A;
  input B;
  input C_N;
  input D_N;
  output Y;
  assign Y = (~A&~B&C_N&D_N);
endmodule

module sky130_fd_sc_hd__nor4bb_4 (A, B, C_N, D_N, Y);
  input A;
  input B;
  input C_N;
  input D_N;
  output Y;
  assign Y = (~A&~B&C_N&D_N);
endmodule

module sky130_fd_sc_hd__o2111a_1 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&B1&C1&D1) | (A2&B1&C1&D1);
endmodule

module sky130_fd_sc_hd__o2111a_2 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&B1&C1&D1) | (A2&B1&C1&D1);
endmodule

module sky130_fd_sc_hd__o2111a_4 (A1, A2, B1, C1, D1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output X;
  assign X = (A1&B1&C1&D1) | (A2&B1&C1&D1);
endmodule

module sky130_fd_sc_hd__o2111ai_1 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1) | (~D1);
endmodule

module sky130_fd_sc_hd__o2111ai_2 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1) | (~D1);
endmodule

module sky130_fd_sc_hd__o2111ai_4 (A1, A2, B1, C1, D1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  input D1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1) | (~D1);
endmodule

module sky130_fd_sc_hd__o211a_1 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1);
endmodule

module sky130_fd_sc_hd__o211a_2 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1);
endmodule

module sky130_fd_sc_hd__o211a_4 (A1, A2, B1, C1, X);
  input A1;
  input A2;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1);
endmodule

module sky130_fd_sc_hd__o211ai_1 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o211ai_2 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o211ai_4 (A1, A2, B1, C1, Y);
  input A1;
  input A2;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o21a_1 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1);
endmodule

module sky130_fd_sc_hd__o21a_2 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1);
endmodule

module sky130_fd_sc_hd__o21a_4 (A1, A2, B1, X);
  input A1;
  input A2;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1);
endmodule

module sky130_fd_sc_hd__o21ai_0 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~A2) | (~B1);
endmodule

module sky130_fd_sc_hd__o21ai_1 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~A2) | (~B1);
endmodule

module sky130_fd_sc_hd__o21ai_2 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~A2) | (~B1);
endmodule

module sky130_fd_sc_hd__o21ai_4 (A1, A2, B1, Y);
  input A1;
  input A2;
  input B1;
  output Y;
  assign Y = (~A1&~A2) | (~B1);
endmodule

module sky130_fd_sc_hd__o21ba_1 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&~B1_N) | (A2&~B1_N);
endmodule

module sky130_fd_sc_hd__o21ba_2 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&~B1_N) | (A2&~B1_N);
endmodule

module sky130_fd_sc_hd__o21ba_4 (A1, A2, B1_N, X);
  input A1;
  input A2;
  input B1_N;
  output X;
  assign X = (A1&~B1_N) | (A2&~B1_N);
endmodule

module sky130_fd_sc_hd__o21bai_1 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&~A2) | (B1_N);
endmodule

module sky130_fd_sc_hd__o21bai_2 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&~A2) | (B1_N);
endmodule

module sky130_fd_sc_hd__o21bai_4 (A1, A2, B1_N, Y);
  input A1;
  input A2;
  input B1_N;
  output Y;
  assign Y = (~A1&~A2) | (B1_N);
endmodule

module sky130_fd_sc_hd__o221a_1 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A1&B2&C1) | (A2&B2&C1);
endmodule

module sky130_fd_sc_hd__o221a_2 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A1&B2&C1) | (A2&B2&C1);
endmodule

module sky130_fd_sc_hd__o221a_4 (A1, A2, B1, B2, C1, X);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A1&B2&C1) | (A2&B2&C1);
endmodule

module sky130_fd_sc_hd__o221ai_1 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2) | (~C1);
endmodule

module sky130_fd_sc_hd__o221ai_2 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2) | (~C1);
endmodule

module sky130_fd_sc_hd__o221ai_4 (A1, A2, B1, B2, C1, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  input C1;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2) | (~C1);
endmodule

module sky130_fd_sc_hd__o22a_1 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A1&B2) | (A2&B2);
endmodule

module sky130_fd_sc_hd__o22a_2 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A1&B2) | (A2&B2);
endmodule

module sky130_fd_sc_hd__o22a_4 (A1, A2, B1, B2, X);
  input A1;
  input A2;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A1&B2) | (A2&B2);
endmodule

module sky130_fd_sc_hd__o22ai_1 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2);
endmodule

module sky130_fd_sc_hd__o22ai_2 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2);
endmodule

module sky130_fd_sc_hd__o22ai_4 (A1, A2, B1, B2, Y);
  input A1;
  input A2;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (~A1&~A2);
endmodule

module sky130_fd_sc_hd__o2bb2a_1 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (~A1_N&B1) | (~A2_N&B1) | (~A1_N&B2) | (~A2_N&B2);
endmodule

module sky130_fd_sc_hd__o2bb2a_2 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (~A1_N&B1) | (~A2_N&B1) | (~A1_N&B2) | (~A2_N&B2);
endmodule

module sky130_fd_sc_hd__o2bb2a_4 (A1_N, A2_N, B1, B2, X);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output X;
  assign X = (~A1_N&B1) | (~A2_N&B1) | (~A1_N&B2) | (~A2_N&B2);
endmodule

module sky130_fd_sc_hd__o2bb2ai_1 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (A1_N&A2_N);
endmodule

module sky130_fd_sc_hd__o2bb2ai_2 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (A1_N&A2_N);
endmodule

module sky130_fd_sc_hd__o2bb2ai_4 (A1_N, A2_N, B1, B2, Y);
  input A1_N;
  input A2_N;
  input B1;
  input B2;
  output Y;
  assign Y = (~B1&~B2) | (A1_N&A2_N);
endmodule

module sky130_fd_sc_hd__o311a_1 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A3&B1&C1);
endmodule

module sky130_fd_sc_hd__o311a_2 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A3&B1&C1);
endmodule

module sky130_fd_sc_hd__o311a_4 (A1, A2, A3, B1, C1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output X;
  assign X = (A1&B1&C1) | (A2&B1&C1) | (A3&B1&C1);
endmodule

module sky130_fd_sc_hd__o311ai_0 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o311ai_1 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o311ai_2 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o311ai_4 (A1, A2, A3, B1, C1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input C1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1) | (~C1);
endmodule

module sky130_fd_sc_hd__o31a_1 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1);
endmodule

module sky130_fd_sc_hd__o31a_2 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1);
endmodule

module sky130_fd_sc_hd__o31a_4 (A1, A2, A3, B1, X);
  input A1;
  input A2;
  input A3;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1);
endmodule

module sky130_fd_sc_hd__o31ai_1 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1);
endmodule

module sky130_fd_sc_hd__o31ai_2 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1);
endmodule

module sky130_fd_sc_hd__o31ai_4 (A1, A2, A3, B1, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1);
endmodule

module sky130_fd_sc_hd__o32a_1 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A1&B2) | (A2&B1) | (A3&B1) | (A2&B2) | (A3&B2);
endmodule

module sky130_fd_sc_hd__o32a_2 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A1&B2) | (A2&B1) | (A3&B1) | (A2&B2) | (A3&B2);
endmodule

module sky130_fd_sc_hd__o32a_4 (A1, A2, A3, B1, B2, X);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output X;
  assign X = (A1&B1) | (A1&B2) | (A2&B1) | (A3&B1) | (A2&B2) | (A3&B2);
endmodule

module sky130_fd_sc_hd__o32ai_1 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1&~B2);
endmodule

module sky130_fd_sc_hd__o32ai_2 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1&~B2);
endmodule

module sky130_fd_sc_hd__o32ai_4 (A1, A2, A3, B1, B2, Y);
  input A1;
  input A2;
  input A3;
  input B1;
  input B2;
  output Y;
  assign Y = (~A1&~A2&~A3) | (~B1&~B2);
endmodule

module sky130_fd_sc_hd__o41a_1 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1) | (A4&B1);
endmodule

module sky130_fd_sc_hd__o41a_2 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1) | (A4&B1);
endmodule

module sky130_fd_sc_hd__o41a_4 (A1, A2, A3, A4, B1, X);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output X;
  assign X = (A1&B1) | (A2&B1) | (A3&B1) | (A4&B1);
endmodule

module sky130_fd_sc_hd__o41ai_1 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3&~A4) | (~B1);
endmodule

module sky130_fd_sc_hd__o41ai_2 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3&~A4) | (~B1);
endmodule

module sky130_fd_sc_hd__o41ai_4 (A1, A2, A3, A4, B1, Y);
  input A1;
  input A2;
  input A3;
  input A4;
  input B1;
  output Y;
  assign Y = (~A1&~A2&~A3&~A4) | (~B1);
endmodule

module sky130_fd_sc_hd__or2_0 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A) | (B);
endmodule

module sky130_fd_sc_hd__or2_1 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A) | (B);
endmodule

module sky130_fd_sc_hd__or2_2 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A) | (B);
endmodule

module sky130_fd_sc_hd__or2_4 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A) | (B);
endmodule

module sky130_fd_sc_hd__or2b_1 (A, B_N, X);
  input A;
  input B_N;
  output X;
  assign X = (A) | (~B_N);
endmodule

module sky130_fd_sc_hd__or2b_2 (A, B_N, X);
  input A;
  input B_N;
  output X;
  assign X = (A) | (~B_N);
endmodule

module sky130_fd_sc_hd__or2b_4 (A, B_N, X);
  input A;
  input B_N;
  output X;
  assign X = (A) | (~B_N);
endmodule

module sky130_fd_sc_hd__or3_1 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A) | (B) | (C);
endmodule

module sky130_fd_sc_hd__or3_2 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A) | (B) | (C);
endmodule

module sky130_fd_sc_hd__or3_4 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A) | (B) | (C);
endmodule

module sky130_fd_sc_hd__or3b_1 (A, B, C_N, X);
  input A;
  input B;
  input C_N;
  output X;
  assign X = (A) | (B) | (~C_N);
endmodule

module sky130_fd_sc_hd__or3b_2 (A, B, C_N, X);
  input A;
  input B;
  input C_N;
  output X;
  assign X = (A) | (B) | (~C_N);
endmodule

module sky130_fd_sc_hd__or3b_4 (A, B, C_N, X);
  input A;
  input B;
  input C_N;
  output X;
  assign X = (A) | (B) | (~C_N);
endmodule

module sky130_fd_sc_hd__or4_1 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A) | (B) | (C) | (D);
endmodule

module sky130_fd_sc_hd__or4_2 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A) | (B) | (C) | (D);
endmodule

module sky130_fd_sc_hd__or4_4 (A, B, C, D, X);
  input A;
  input B;
  input C;
  input D;
  output X;
  assign X = (A) | (B) | (C) | (D);
endmodule

module sky130_fd_sc_hd__or4b_1 (A, B, C, D_N, X);
  input A;
  input B;
  input C;
  input D_N;
  output X;
  assign X = (A) | (B) | (C) | (~D_N);
endmodule

module sky130_fd_sc_hd__or4b_2 (A, B, C, D_N, X);
  input A;
  input B;
  input C;
  input D_N;
  output X;
  assign X = (A) | (B) | (C) | (~D_N);
endmodule

module sky130_fd_sc_hd__or4b_4 (A, B, C, D_N, X);
  input A;
  input B;
  input C;
  input D_N;
  output X;
  assign X = (A) | (B) | (C) | (~D_N);
endmodule

module sky130_fd_sc_hd__or4bb_1 (A, B, C_N, D_N, X);
  input A;
  input B;
  input C_N;
  input D_N;
  output X;
  assign X = (A) | (B) | (~C_N) | (~D_N);
endmodule

module sky130_fd_sc_hd__or4bb_2 (A, B, C_N, D_N, X);
  input A;
  input B;
  input C_N;
  input D_N;
  output X;
  assign X = (A) | (B) | (~C_N) | (~D_N);
endmodule

module sky130_fd_sc_hd__or4bb_4 (A, B, C_N, D_N, X);
  input A;
  input B;
  input C_N;
  input D_N;
  output X;
  assign X = (A) | (B) | (~C_N) | (~D_N);
endmodule

module sky130_fd_sc_hd__probe_p_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__probec_p_8 (A, X);
  input A;
  output X;
  assign X = (A);
endmodule

module sky130_fd_sc_hd__sdfrtn_1 (CLK_N, D, RESET_B, SCD, SCE, Q);
  input CLK_N;
  input D;
  input RESET_B;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfrtp_1 (CLK, D, RESET_B, SCD, SCE, Q);
  input CLK;
  input D;
  input RESET_B;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfrtp_2 (CLK, D, RESET_B, SCD, SCE, Q);
  input CLK;
  input D;
  input RESET_B;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfrtp_4 (CLK, D, RESET_B, SCD, SCE, Q);
  input CLK;
  input D;
  input RESET_B;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfstp_1 (CLK, D, SCD, SCE, SET_B, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfstp_2 (CLK, D, SCD, SCE, SET_B, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfstp_4 (CLK, D, SCD, SCE, SET_B, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  input SET_B;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfxtp_1 (CLK, D, SCD, SCE, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfxtp_2 (CLK, D, SCD, SCE, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdfxtp_4 (CLK, D, SCD, SCE, Q);
  input CLK;
  input D;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sdlclkp_1 (CLK, GATE, SCE, GCLK);
  input CLK;
  input GATE;
  input SCE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__sdlclkp_2 (CLK, GATE, SCE, GCLK);
  input CLK;
  input GATE;
  input SCE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__sdlclkp_4 (CLK, GATE, SCE, GCLK);
  input CLK;
  input GATE;
  input SCE;
  output GCLK;
  assign GCLK = (CLK*M0);
endmodule

module sky130_fd_sc_hd__sedfxtp_1 (CLK, D, DE, SCD, SCE, Q);
  input CLK;
  input D;
  input DE;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sedfxtp_2 (CLK, D, DE, SCD, SCE, Q);
  input CLK;
  input D;
  input DE;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__sedfxtp_4 (CLK, D, DE, SCD, SCE, Q);
  input CLK;
  input D;
  input DE;
  input SCD;
  input SCE;
  output Q;
  assign Q = IQ;
endmodule

module sky130_fd_sc_hd__xnor2_1 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B) | (A&B);
endmodule

module sky130_fd_sc_hd__xnor2_2 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B) | (A&B);
endmodule

module sky130_fd_sc_hd__xnor2_4 (A, B, Y);
  input A;
  input B;
  output Y;
  assign Y = (~A&~B) | (A&B);
endmodule

module sky130_fd_sc_hd__xnor3_1 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (~A&~B&~C) | (A&B&~C) | (A&~B&C) | (~A&B&C);
endmodule

module sky130_fd_sc_hd__xnor3_2 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (~A&~B&~C) | (A&B&~C) | (A&~B&C) | (~A&B&C);
endmodule

module sky130_fd_sc_hd__xnor3_4 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (~A&~B&~C) | (A&B&~C) | (A&~B&C) | (~A&B&C);
endmodule

module sky130_fd_sc_hd__xor2_1 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&~B) | (~A&B);
endmodule

module sky130_fd_sc_hd__xor2_2 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&~B) | (~A&B);
endmodule

module sky130_fd_sc_hd__xor2_4 (A, B, X);
  input A;
  input B;
  output X;
  assign X = (A&~B) | (~A&B);
endmodule

module sky130_fd_sc_hd__xor3_1 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&~B&~C) | (~A&B&~C) | (~A&~B&C) | (A&B&C);
endmodule

module sky130_fd_sc_hd__xor3_2 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&~B&~C) | (~A&B&~C) | (~A&~B&C) | (A&B&C);
endmodule

module sky130_fd_sc_hd__xor3_4 (A, B, C, X);
  input A;
  input B;
  input C;
  output X;
  assign X = (A&~B&~C) | (~A&B&~C) | (~A&~B&C) | (A&B&C);
endmodule
