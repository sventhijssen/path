module example (
    a, b, c, f);
  input  a, b, c;
  output f;
  assign f = (a & b & c) | (~a & ~b & c) | (~a & b);
endmodule

