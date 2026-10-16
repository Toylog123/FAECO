module top(A,B,CIN,SUM,COUT);
input A,B,CIN;
output SUM,COUT;
assign SUM=A^B^CIN;
assign COUT=(A&B)|(A&CIN)|(B&CIN);
endmodule