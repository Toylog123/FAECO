module top(A,TE_B,Z);
input A,TE_B;
output Z;
assign Z=TE_B ? 1'bz : ~A;
endmodule
