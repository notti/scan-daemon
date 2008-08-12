import worker
import pyx
from PIL import Image
import os

class picture2pdf(worker.work):
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
        c.insert(pyx.bitmap.bitmap(0, 0, Image.open(self.im), pyx.document.paperformat.A4.width, pyx.document.paperformat.A4.height, compressmode=self.compressmode, dctquality=self.dctquality, flatecompresslevel=self.flatecompresslevel))
        os.unlink(self.im)
        p = pyx.document.page(c)
        self.doc.insert(self.page,p)

def makepdf(filename, pages):
    d = pyx.document.document(pages)
    d.writePDFfile(filename)
    del d

