module toy(a,b,c,n6);
input a,b,c;
output n6;
wire n1,n2,n3,n4,n5;
sky130_fd_sc_hd__clkinv_1 g1 (.A(a), .Y(n1));
sky130_fd_sc_hd__clkinv_1 g2 (.A(b), .Y(n2));
sky130_fd_sc_hd__nor2_1 g3 (.A(c), .B(c), .Y(n3));
sky130_fd_sc_hd__and2_1 g4 (.A(n1), .B(n2), .X(n4));
sky130_fd_sc_hd__or2_1 g5 (.A(n2), .B(n3), .X(n5));
sky130_fd_sc_hd__nor2_1 g6 (.A(n4), .B(n5), .Y(n6));
endmodule
