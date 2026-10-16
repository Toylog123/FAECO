module top(A,B,CIN,SUM,COUT);
input A,B,CIN;
output SUM,COUT;
sky130_fd_sc_hd__fa_1 g(.A(A),.B(B),.CIN(CIN),.SUM(SUM),.COUT(COUT));
endmodule