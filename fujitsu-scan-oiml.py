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

num_worker_threads = 3
dct_quality = 30
destination = '/home/notti/'

class work:
    def doIt(self):
        pass

class picture2pdf(work):
    def __init__(self, im, doc, page, compressmode):
        self.doc            = doc
        self.page           = page
        self.im             = im
        self.compressmode   = compressmode
    def doIt(self):
        c = pyx.canvas.canvas
        c.insert(pyx.bitmap.bitmap(0, 0, self.im, pyx.document.paperformat.A4.width, pyx.document.paperformat.A4.height, compressmode=self.compressmode, dctquality=dct_quality))
        del self.im
        p = pyx.document.page(c)
        self.doc.insert(self.page,p)

class picture2file(work):
    def __init__(self, im, doc, page):
        self.im             = im
        self.doc            = doc
        self.page           = page
    def doIt(self):
        self.im.save(self.doc.filename(self.page))
        del self.im

class document:
    def __init__(self, targetfile=None, format="pdf"):
        if targetfile=None:
            self.targetfile="%s/scan-%d" % (destination, int(time.time))
        else:
            self.targetfile=targetfile
        self.format     = format
        self.pages      = []
        self.pagenumber = 1

    def filename(self, page=None):
        if page=None:
            return "%s.%s" % (self.targetfile,self.format)
        else
            return "%s-%d.%s" % (self.targetfile,page,self.format)

    def process_image(self, im):
        if self.format = "pdf":
            w = picture2pdf(im, self, self.pagenumber, "DCT")
        else:
            w = picture2file(im, self, self.pagenumber)
        self.pagenumber = self.pagenumber + 1
        return w

    def insert(self, pagenumber, page):
        pass

    def finalize(self):
        pass


# =-=-=-=-=-=-= MAIN =-=-=-=-=-=-=-=

sane.init()
s = sane.open(sane.get_devices()[0][0])

work_queue = Queue.Queue()
def worker():
    while True:
        item = work_queue.get()
        item.doIt()
        work_queue.task_done()

for i in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.start()


doc = None

try:
    while True:
        pressed_scan = 0
        pressed_send = 0
        while not (pressed_scan or pressed_send):
            pressed_scan = s.button_scan
            pressed_send = s.button_send
            time.sleep(2)

        x = s.button_function
        #1: Color Duplex 150
        #2: Color Duplex 300
        #3: Color 150
        #4: Color 300
        #5: Gray Duplex 150
        #6: Gray Duplex 300
        #7: Gray 150
        #8: Gray 300
        #9: Color 600 (tiff)
        #10:Color Duplex 600 (tiff)
        if x >= 1 and x <= 4 or x == 9 or x == 10:
            s.mode = 'Color'
        else:
            s.mode = 'Gray'

        if x == 2 or x == 4 or x == 6 or x == 8:
            s.resolution = 300
        elif x == 9 or x == 10:
            s.resolution = 600
        else:
            s.resolution = 150
            
        if x == 1 or x == 2 or x == 5 or x == 6 or x == 10:
            s.source = 'ADF Duplex'
        else:
            s.source = 'ADF Front'
        
        if doc=None:
            if x == 9 or x == 10:
                format="tiff"
            else:
                format="pdf"
            doc=document(format=format)

        # we want a4
        s.pageheight = 297
        s.pagewidth = 210
        s.br_y = 297
        s.br_x = 210

        for im in s.multi_scan():
            q.put(doc.process_image(im))

        if pressed_scan:
            doc.finalize()
            del doc
            doc = None

finally:
    s.cancel()
    q.join()
    if doc:
        doc.finalize()
    s.close()

