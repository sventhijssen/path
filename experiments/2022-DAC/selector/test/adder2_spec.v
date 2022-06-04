// Benchmark "adder2" written by ABC on Wed Oct 27 16:11:04 2021

module adder2 ( 
    a1, a0, b1, b0, cin,
    cout, s1, s0  );
  input  a1, a0, b1, b0, cin;
  output cout, s1, s0;
  assign cout = (((a0 & (b0 | cin)) | (b0 & cin)) & (a1 | b1)) | (a1 & b1);
  assign s1 = ((~a1 ^ b1) & ((a0 & (b0 | cin)) | (b0 & cin))) | (((~b0 & ~cin) | (~a0 & (~b0 | ~cin))) & (a1 ^ b1));
  assign s0 = a0 ? (b0 ^ ~cin) : (b0 ^ cin);
endmodule


