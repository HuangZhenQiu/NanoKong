import java.io.*;
import nanovm.avr.*;
import nanovm.io.*;

class TestNvmCommRot13 {
  private static void Rot13(byte[] data) {
    for (int i = 0; i < data.length; i++) {
      byte c = data[i];
      System.out.println(c);
      if      (c >= 'a' && c <= 'm') c += 13;
      else if (c >= 'n' && c <= 'z') c -= 13;
      else if (c >= 'A' && c <= 'M') c += 13;
      else if (c >= 'N' && c <= 'Z') c -= 13;
      data[i] = c;
    }
  }
  
  public static void main(String[] args) throws IOException {
    while(true) {
      System.out.println("Waiting for data.....");
      byte[] data = NvmComm.receive(1000);
      if (data != null) {
        Rot13(data);
        NvmComm.send((byte)2, data, (byte)data.length);
      }
    }
  }
}

     
