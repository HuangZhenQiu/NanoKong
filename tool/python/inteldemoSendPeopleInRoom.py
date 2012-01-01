#!/usr/bin/python

import sys
import pynvc3

def testLamp(destination, input):
  if input == "On":
    pynvc3.sendcmd(destination, pynvc3.APPMSG, [5, 1])
  elif input == "Off":
    pynvc3.sendcmd(destination, pynvc3.APPMSG, [5, 0])
  else:
    print "inteldemoSendPeopleInRoom <nodeid> [On|Off]"

pynvc3.init()
testLamp(int(sys.argv[1]), sys.argv[2] if len(sys.argv)>2 else "Off")