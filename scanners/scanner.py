import sane, time, threading

class scanner:
    def __init__(self, config):
        self.config = config

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def set_parameters(self, scanner, mode, source, resolution):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        pass

    def serve_forever(self):
        pass

class direct_scanner(scanner):
    def __init__(self, config):
        scanner.__init__(self, config)
        self.connected = False
        self.event = threading.Event()

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def set_parameters(self, scanner, mode, source, resolution):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        if status == "connected":
            self.event.set()
        elif status == "disconnected":
            self.connected = False
            self.event.set()

    def attach_scanner(self, name):
        for i in range(2):
            print "checking ..."
            for device in sane.get_devices():
                print device[2]
                if device[2] == name:
                    return sane.open(device[0])
            self.event.wait(1)
        return None

    def scan(self, buttons_pressed=None, doc=None):
        pass

    def serve_forever(self):
        scanner = self.attach_scanner(self.name)
        while True:
            while scanner == None:
                self.event.wait(20)
                self.event.clear()
                scanner = self.attach_scanner(self.name)
            print "connected"
            self.connected = True
            while self.connected:
                buttons_pressed = self.wait_for_button(scanner)
                if buttons_pressed == None:
                    scanner = None
                    break
                self.scan(buttons_pressed)

