import nanovm.avr.*;
import nanovm.io.*;

class ZZTrafficLightNormal {
    public static void flashLed(int pin, int times, int wait){
        for (int i = 0; i < times; i++) {
            AVR.digitalWrite(pin, AVR.HIGH);
            Timer.wait(wait);
            AVR.digitalWrite(pin, AVR.LOW);
            
            if (i + 1 < times) {
                Timer.wait(wait);
            }
        } 
    }
    public static void main(String[] args) {
        int[] pins = {AVR.DIGITAL13, AVR.DIGITAL32, AVR.DIGITAL33, AVR.DIGITAL34}; // Green, Yellow, Red, Session Lights
        int[] intervals = {50, 2500, 1000, 1500};
        int[] times = {2, 1, 1, 1};
        for (int i : pins){
            AVR.setPinIOMode(i, AVR.OUTPUT);
            AVR.digitalWrite(i, AVR.LOW);
        }
        System.out.println("This is traffic light normal mode.....");
        while(true) {
            /* Green -> Yellow -> Red */
            for (int i = 0; i < pins.length; ++i)
                flashLed(pins[i], times[i], intervals[i]);            
        }
    }
}
