module top(A,B,CIN,SUM,COUT);
input A,B,CIN;
output SUM,COUT;
wire unused_carry;
assign COUT=1'b0;
sky130_fd_sc_hd__fa_1 g(.A(A),.B(B),.CIN(CIN),.SUM(SUM),.COUT(unused_carry));
endmodule
