module example (
    a, b, c, f);
  input  a, b, c, d, e;
  output f;
  assign f = (a & b & c & e) | (a & ~b & d & e) | (~a & b & ~e) | (~a & ~b & ~d & ~e);
endmodule

