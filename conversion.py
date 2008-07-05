import worker

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
        self.im.save(self.doc.filename(self.page))
        del self.im

