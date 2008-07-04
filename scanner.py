#!/usr/bin/python

import sane
import time
import signal
import os
import threading
import subprocess
import glob
import ExitQueue
import pyx
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(['scanner.cfg','/etc/scanner.cf'])

num_worker_threads = config.getint('Default','worker_threads')
default_dct_quality = config.getint('Default','dct_quality')
default_flatecompresslevel = config.getint('Default','flatecompresslevel')
default_compressmode = config.get('Default','compressmode')
if default_compressmode == 'None':
    default_compressmode = None
default_scanner = config.get('Default','scanner')
destination = config.get('Default', 'destination')


class work:
    """Base class for doin' all the work
       It's used to enqueue the thing and do the work in some worker threads"""
    def doIt(self):
        pass

class picture2pdf(work):
    """Takes a PIL image and converts it to Postscript Page

       Attributes:
            im          PIL image
            doc         Document
            page        Page number
            compressmode Compression Mode ("DCT", "Flate", none)
            dctquality  Quality for DCT compression
            flatecompresslevel  zlib compresslevel"""
    def __init__(self, im, doc, page, compressmode, dctquality, flatecompresslevel):
        self.doc            = doc
        self.page           = page
        self.im             = im
        self.compressmode   = compressmode
        self.dctquality     = dctquality
        self.flatecompresslevel = flatecompresslevel
    def doIt(self):
        c = pyx.canvas.canvas()
        c.insert(pyx.bitmap.bitmap(0, 0, self.im, pyx.document.paperformat.A4.width, pyx.document.paperformat.A4.height, compressmode=self.compressmode, dctquality=self.dctquality, flatecompresslevel=self.flatecompresslevel))
        del self.im
        p = pyx.document.page(c)
        self.doc.insert(self.page,p)

class picture2file(work):
    """Takes a PIL image and stores it to the filesystem

       Attributes:
            im          PIL image
            doc         Document
            page        Page number"""
    def __init__(self, im, doc, page):
        self.im             = im
        self.doc            = doc
        self.page           = page
    def doIt(self):
        self.im.save(self.doc.filename(self.page))
        del self.im

class outDocument(work):
    """Takes a document and finalizes it

       Attributes:
            doc         Document"""
    def __init__(self, doc):
        self.doc            = doc
    def doIt(self):
        self.doc.finalize()
        del self.doc

class document:
    """Class representing a document"""
    def __init__(self, targetfile=None, format="pdf"):
        if targetfile == None:
            self.targetfile="%s/scan-%d" % (destination, int(time.time()))
        else:
            self.targetfile=targetfile
        self.format         = format
        self.pages          = []
        self.pagenumber     = 0
        self.in_conversion  = 0
        self.conversion_condition = threading.Condition()

    def filename(self, page=None):
        if page == None:
            return "%s.%s" % (self.targetfile,self.format)
        else:
            return "%s-%d.%s" % (self.targetfile,page,self.format)

    def process_image(self, im):
        if self.format == "pdf":
            w = picture2pdf(im, self, self.pagenumber, default_compressmode, default_dct_quality, default_flatecompresslevel)
            self.pages.append(None)
        else:
            w = picture2file(im, self, self.pagenumber+1)
        self.pagenumber = self.pagenumber + 1
        self.conversion_condition.acquire()
        self.in_conversion = self.in_conversion + 1
        self.conversion_condition.release()
        return w

    def insert(self, pagenumber, page):
        self.pages[pagenumber] = page
        self.conversion_condition.acquire()
        self.in_conversion = self.in_conversion - 1
        self.conversion_condition.notify()
        self.conversion_condition.release()

    def finalize(self):
        self.conversion_condition.acquire()
        while self.in_conversion:
            self.conversion_condition.wait()
        print self.pages
        d = pyx.document.document(self.pages)
        print self.filename()
        d.writePDFfile(self.filename())
        del self.pages
        self.conversion_condition.release()


# =-=-=-=-=-=- WORKER -=-=-=-=-=-=-=

work_queue = ExitQueue.Queue()

def worker():
    try:
        while True:
            item = work_queue.get()
            item.doIt()
            work_queue.task_done()
    except ExitQueue.Exit:
        pass

for i in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.start()

# =-=-=-=-= START STOP =-=-=-=-=-=-=

class ScannerPlugged(Exception):
    pass

class ScannerUnPlugged(Exception):
    pass

def start_stop_service(num, frame):
    if num == signal.SIGUSR1: # scanner plugged in
        raise ScannerPlugged
    elif num == signal.SIGUSR2: # scanner unplugged
        raise ScannerUnPlugged

signal.signal(signal.SIGUSR1, start_stop_service)
signal.signal(signal.SIGUSR2, start_stop_service)

# =-=-=-=-=-=-= MAIN =-=-=-=-=-=-=-=

sane.init()

def get_scanner_device():
    try:
        s = None
        for dev in sane.get_devices():
            if dev[2] == default_scanner:
                s = dev[0]
                break
        if s == None:
            return None
        s = sane.open(s)
        return s
    except KeyboardInterrupt:
        raise
    except:
           pass     #talk to bajo that something is not working
    return None

def pause_until_scanner():
    s = get_scanner_device()
    while s == None:
        try:
            signal.pause()
        except ScannerUnPlugged, ScannerPlugged:
            pass
        s = get_scanner_device()
    return s

doc = None
scanner = None

# let's look if scanner is there
try:
    while True:
        while scanner == None:
            scanner = pause_until_scanner()

        try:
            # start the button polling
            while True:
                pressed_scan = 0
                pressed_send = 0
                while not (pressed_scan or pressed_send):
                    pressed_scan = scanner.button_scan
                    pressed_send = scanner.button_send
                    time.sleep(2)
                function = scanner.button_function


                scanner.mode       = default_buttons[function][0]
                scanner.source     = default_buttons[function][1]
                scanner.resolution = default_buttons[function][2]
                scanner.pageheight = 297
                scanner.pagewidth = 210
                scanner.br_y = 297
                scanner.br_x = 210

                if doc == None:
                    doc=document(format=default_buttons[function][3])

                for im in scanner.multi_scan():
                    w = doc.process_image(im)
                    work_queue.put(w)

                if pressed_scan:
                    work_queue.put(outDocument(doc))
                    doc = None
        except KeyboardInterrupt:
            break
#        except:
#            pass
finally:
    scanner.cancel()
    work_queue.close()
    if doc:
        doc.finalize()
    scanner.close()

