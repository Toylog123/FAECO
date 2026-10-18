module top(a, \a[0] , z1, z2);
input [1:0] a; input \a[0] ; output z1,z2;
sky130_fd_sc_hd__buf_1 b1 (.A(a[0]),.X(z1));
sky130_fd_sc_hd__buf_1 b2 (.A(\a[0] ),.X(z2));
endmodule