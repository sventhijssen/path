module example (
    a, b, c, d, f);
  input  a, b, c, d;
  output f;
  assign f = (a & c & d) | (~a & ~b & ~c & d) | (~a & ~b & c & ~d);
endmodule

