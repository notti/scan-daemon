# Copyright (c) 2008 Gernot Vormayr <notti@fet.at>
#
# This file is part of scan-daemon.
# 
# scan-daemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# scan-daemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
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

