module top(CLK,D,DE,Q);
input CLK,D,DE;
output reg Q;
always @(posedge CLK) if (DE) Q<=D;
endmodule
