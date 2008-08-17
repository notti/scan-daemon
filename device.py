import time, threading, usbdevice, syslog
import subprocess, glob
import document

class scanners:
    def __init__(self, config):
        self.config = config
        devices = []
        for device in glob.iglob('devices/*py'):
            try:
                dev = __import__(device[:-3]).devices
            except:
                syslog.syslog(syslog.LOG_WARNING,'Could not load '+device)
            else:
                devices += zip(dev.keys(), dev.values())

        devices = dict(devices)

        self.scanners = {}
        for scanner in config.scanner.split(','):
            scanner = scanner.strip()
            try:
                self.scanners[scanner] = devices[scanner](config)
            except KeyError:
                syslog.syslog(syslog.LOG_ERR,"Couldn't find scanner '%s'!" % scanner)

    def status_change(self, scanner, status):
        self.scanners[scanner].status_change(status)

    def serve_forever(self):
        for name, scanner in self.scanners.iteritems():
            t = threading.Thread(target = scanner.serve_forever, name = name)
            t.start()

    def shutdown(self):
        syslog.syslog(syslog.LOG_INFO, 'shutting down...')
        for name, scanner in self.scanners.iteritems():
            scanner.shutdown()
        syslog.syslog(syslog.LOG_INFO, 'shutdown complete.')

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
        self.timer = 0
        self.running = True

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        if status == 'connected':
            self.event.set()
        elif status == 'disconnected':
            self.connected = False
            self.event.set()

    def attach_scanner(self):
        for i in range(2):
            if self.running == False:
                return False
            try:
                self.claim()
                return True
            except:
                self.event.wait(1)
        return False

    def read_buttons(self):
        return {}

# XXX targetfile
    def scan(self, params):
        finish = params['document-finish']
        document_type = params['document-type']
        del params['document-type']
        del params['document-finish']
        params['output-file'] = self.name+'-scan-%04d'
        params['d'] = self.get_sane_name()
        command = ['/usr/bin/scanadf']
        for option, value in params.iteritems():
            if len(option) == 1:
                command.append('-'+option)
            else:
                command.append('--'+option)
            if len(value):
                command.append(value)
        self.unclaim()
        scanadf = subprocess.Popen(command, cwd='/dev/shm', stderr=subprocess.PIPE)
        if self.doc == None:
            self.doc = document.document(self.config, format=document_type)
        error = False
        for line in scanadf.stderr:
            msg = line.strip().split(' ')
            if msg[0] == 'scanadf:':
                error = True
                break
            if len(msg) == 3:
                if msg[1] == 'document':
                    self.doc.process_image('/dev/shm/'+msg[2])
        if (not error) and finish:
            self.doc.finish()
            self.doc = None
        else:
            self.timer = 0
        scanadf.wait()
        self.claim()

    def get_sane_name(self):
        return ''

    def reset_document(self):
        if self.doc != None:
            self.timer = self.timer + 1
            if self.timer > 15:
                self.doc.finish()
                self.doc = None

    def shutdown(self):
        self.running    = False
        self.connected  = False
        self.event.set()

    def serve_forever(self):
        self.connected = self.attach_scanner()
        while self.running:
            while self.connected == False and self.running == True:
                self.event.wait(20)
                self.event.clear()
                self.connected = self.attach_scanner()
            while self.connected:
                buttons_pressed = self.wait_for_button(scanner)
                if buttons_pressed == None:
                    self.connected = False
                    break
                self.scan(buttons_pressed)
        if self.doc != None:
            self.doc.finish()

