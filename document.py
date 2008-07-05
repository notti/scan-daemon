import threading, time
import pdf, worker, conversion
from __future__ import with_statement

class outDocument(worker.work):
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
    def __init__(self, targetfile=None, format="pdf", maxconversion=0):
        if targetfile == None:
            self.targetfile="%s/scan-%d" % (destination, int(time.time()))
        else:
            self.targetfile=targetfile
        self.format         = format
        self.pages          = []
        self.pagenumber     = 0
        self.in_conversion  = 0
        self.conversion_condition = threading.Condition()
        self.maxconversion  = maxconversion

    def filename(self, page=None):
        if page == None:
            return "%s.%s" % (self.targetfile,self.format)
        else:
            return "%s-%d.%s" % (self.targetfile,page,self.format)

    def process_image(self, im):
        if self.format == "pdf":
            w = pdf.picture2pdf(im, self, self.pagenumber, default_compressmode, default_dct_quality, default_flatecompresslevel)
            self.pages.append(None)
        else:
            w = conversion.picture2file(im, self, self.pagenumber+1)
        self.pagenumber = self.pagenumber + 1
        with self.conversion_condition:
            if self.maxconversion:
                while self.in_conversion >= self.maxconversion:
                    self.conversion_condition.wait()                
            self.in_conversion = self.in_conversion + 1
        return w

    def insert(self, pagenumber, page):
        self.pages[pagenumber] = page
        with self.conversion_condition:
            self.in_conversion = self.in_conversion - 1
            self.conversion_condition.notifyAll()

    def finalize(self):
        with self.conversion_condition:
            while self.in_conversion:
                self.conversion_condition.wait()
            pdf.makepdf(self.filename(), self.pages)
            del self.pages

