module helper(A,Y);
 input A;
 output Y;
 sky130_fd_sc_hd__buf_1 x(.A(A),.X(Y));
 endmodule
module top(A,Y,Z);
  wire n_x;
  wire n_y;
 input A;
 output Y,Z;
 sky130_fd_sc_hd__buf_1 x (.A(n_x),.X(Y));
 sky130_fd_sc_hd__buf_1 y (.A(n_y),.X(Z));
   sky130_fd_sc_hd__buf_1 _bufb_x_A (
    .A(A),
    .X(n_x)
  );
  sky130_fd_sc_hd__buf_1 _bufb_y_A (
    .A(A),
    .X(n_y)
  );
endmodule