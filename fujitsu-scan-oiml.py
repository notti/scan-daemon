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

class document:
    def __init__(self, targetfile, format):
        self.targetfile = targetfile
        self.format     = format
        self.pages      = []

    class page:
        def __init__(self, timestamp, number, resolution, colorspace, parent)
            self.timestamp  = timestamp
            self.number     = number
            self.resolution = resolution
            self.colorspace = colorspace
            self.parent     = parent




signal.signal(signal.SIGQUIT,handler)

sane.init()

s = sane.open(sane.get_devices()[0][0])


def image_converter():
    while True:
        item = q.get()
        if item.endswith(".jpg"):
            subprocess.call(["convert",item,item+".pdf"])
            os.unlink(item)
        else:
            files = glob.glob('/tmp/'+item.rsplit('/',1)[1].rsplit('.',2)[0]+'*pdf')
            subprocess.call(["gs","-sOutputFile="+item, "-sPAPERSIZE=a4", "-sDEVICE=pdfwrite", "-dBATCH", "-dNOPAUSE", "-dPDFFitPage"]+files)
            for file in files:
                os.unlink(file)
        q.task_done()

q = Queue.Queue()
for i in range(num_worker_threads):
    t = threading.Thread(target=image_converter)
    t.setDaemon(True)
    t.start()

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

        if x == 9 or x == 10:
            file = destination+'%d-scan%d.tiff'
        else:
            file = '/tmp/%d-scan%d.jpg'

        # we want a4
        s.pageheight = 297
        s.pagewidth = 210
        s.br_y = 297
        s.br_x = 210

        timestamp = int(time.time())

        i=0
        for im in s.multi_scan():
            i=i+1 
            name = file % (timestamp,i)
            im.save(name)
            q.put(name)
        q.join()
        if not(x == 9 or x == 10):
            q.put(final+'%d-scan.pdf' % timestamp)

finally:
    q.join()
    s.cancel()
    s.close()

