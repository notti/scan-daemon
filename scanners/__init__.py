import sane

import fujitsu
scanners = {'fi-5110Cdj': fujitsu.fi_5110Cdj}

sane.init()

class scanner:
    def __init__(self, name, maxjobs=None):
        self.scanner        = scanners[name]()
        self.maxjobs        = maxjobs
        self.sane_device    = None

    def disconnect(self):
        pass
    
    def run(self):
        pass

    def connect(self):
        pass
        
    def generate_doc(self):
        pass

    def append_doc(self, doc):
        pass

    def get_dir(self, dir="/"):
        pass


