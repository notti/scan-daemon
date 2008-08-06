#!/usr/bin/python

import usb
import time

class USBDevice:
    def __init__(self):
        self.device = self.find_device()
        self.handle = None

    def find_device(self):
        for bus in usb.busses():
            for device in bus.devices:
                if device.idVendor == 0x04c5 and device.idProduct == 0x1097:
                    return device
        return None

    def claim(self):
        self.handle = self.device.open()
        self.handle.claimInterface(0)

    def unclaim(self):
        self.handle.releaseInterface()

    def getDataPacket(self):
        self.handle.bulkWrite(0x02, '\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00')
        data   = self.handle.bulkRead(0x81, 12)
        status = self.handle.bulkRead(0x81, 13)
        print "function:", data[5]
        print "send sw:", (data[4]>>2)&1
        print "scan sw:", (data[4])&1
        print "paper partly:", (data[2]>>7)&1 #topedge
        print "a3:", (data[2]>>3)&1 #a3
        print "b4:", (data[2]>>2)&1 #b4
        print "a4", (data[2]>>1)&1 #a4
        print "b5", (data[2])&1 #b5
        print "not adf loaded:", (data[3]>>7)&1 #adfloaded
        print "omr double feed", (data[3]>>6)&1 #OMR or double feed
        print "adf open", (data[3]>>5)&1 #adf open
        print "powersave", (data[4]>>7)&1 #powersave
        print "doublefeed", (data[6])&1 #doublefeed
        print "errorcode", data[7] #errorcode
        print "----------------------------"

dev = USBDevice()
dev.claim()
try:
    while True:
        dev.getDataPacket()
        time.sleep(2)
except:
    raise
finally:
    dev.unclaim()

