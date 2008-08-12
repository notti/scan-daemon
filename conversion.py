import worker
from PIL import Image
import os

class picture2file(worker.work):
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
        im = Image.open(self.im)
        im.save(self.doc.filename(self.page))
        os.unlink(self.im)
        del self.im
        os.chmod(self.doc.filename(self.page), 0664)
