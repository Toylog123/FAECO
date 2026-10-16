module top(A,TE,Z);
input A,TE;
output Z;
assign Z=TE ? ~A : 1'bz;
endmodule
