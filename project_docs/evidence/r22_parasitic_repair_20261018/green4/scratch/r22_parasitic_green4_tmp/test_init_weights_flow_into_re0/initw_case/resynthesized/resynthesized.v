module top(A, B, C, D, E, F, G, H, Y);
  input A, B, C, D, E, F, G, H;
  output Y;
  wire N1, N2, N3, N4, N5, N6;
  and g1 (N1, A, B);
  and g2 (N2, C, D);
  and g3 (N3, E, F);
  and g4 (N4, G, H);
  or g5 (N5, N1, N2);
  or g6 (N6, N3, N4);
  or g7 (Y, N5, N6);
endmodule
