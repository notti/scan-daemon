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
import time, threading, usbdevice, syslog, os, signal
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
        self.scanadf = None
        self.id = 0

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
        params['output-file'] = self.name+'-scan-'+str(self.id)+'-%04d'
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
        self.scanadf = subprocess.Popen(command, cwd='/dev/shm', stderr=subprocess.PIPE, bufsize=1)
        if self.doc == None:
            self.doc = document.document(self.config, format=document_type)
        error = False
        while True:
            line = self.scanadf.stderr.readline()
            if not line:
                break
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
        self.scanadf.wait()
        self.scanadf = None
        self.claim()
        self.id = self.id + 1

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
        if self.scanadf != None:
            os.kill(self.scanadf.pid, signal.SIGTERM)

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

