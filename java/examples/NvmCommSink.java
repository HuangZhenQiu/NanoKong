import nanovm.avr.*;
import nanovm.io.*;

class NvmCommSink {
    public static void main(String[] args) {
        System.out.println("Waiting for data.....");
        while(true) {
            byte[] data = NvmComm.receive(1000);
            if (data != null) {
                for (int i = 0; i < data.length; ++i)
                    System.out.print(data[i]);
                System.out.print('\n');
            }
            //Timer.wait(1500);
        }
    }
}
