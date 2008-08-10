import usb

class usb_device:
    def __init__(self):
        self.device = None
        self.handle = None
        self.dirname = ''
        self.filename = ''

    def find_device(self):
        for bus in usb.busses():
            for device in bus.devices:
                if device.idVendor == self.USB_ID_VENDOR and device.idProduct == self.USB_ID_PRODUCT:
                    return (device, bus.dirname, device.filename)
        return None

    def claim(self):
        (self.device, self.dirname, self.filename) = self.find_device()
        self.handle = self.device.open()
        self.handle.claimInterface(0)

    def unclaim(self):
        self.handle.releaseInterface()

    def send(self,packet):
        self.handle.bulkWrite(self.IN_ENDPOINT, packet)

    def recieve(self, bytes):
        return self.handle.bulkRead(self.OUT_ENDPOINT,bytes)

    def get_address(self):
        return 'libusb:'+self.dirname+':'+self.filename

