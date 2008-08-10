import time, threading, usbdevice

class scanner:
    def __init__(self, config):
        self.config = config

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        pass

    def serve_forever(self):
        pass

class usb_scanner(scanner,usbdevice.usb_device):
    def __init__(self, config):
        scanner.__init__(self, config)
        usbdevice.usb_device.__init__(self)
        self.connected = False
        self.event = threading.Event()
        self.doc = None

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        if status == "connected":
            self.event.set()
        elif status == "disconnected":
            self.connected = False
            self.event.set()

    def attach_scanner(self):
        for i in range(2):
            try:
                self.claim()
                return True
            except:
                self.event.wait(1)
        return False

    def read_buttons(self):
        return {}

    def scan(self, finish = True):
        pass

    def serve_forever(self):
        self.connected = self.attach_scanner()
        while True:
            while self.connected == False:
                self.event.wait(20)
                self.event.clear()
                self.connected = self.attach_scanner()
            while self.connected:
                buttons_pressed = self.wait_for_button(scanner)
                if buttons_pressed == None:
                    self.connected = False
                    break
                self.scan(buttons_pressed)

