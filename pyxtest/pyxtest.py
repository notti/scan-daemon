#!/usr/bin/python

import sane
from pyx import *


import os

_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
              'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey):
    '''Private.
    '''
    global _proc_status, _scale
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
    # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


sane.init()

s = sane.open(sane.get_devices()[0][0])


s.mode = 'Color'

s.resolution = 300
s.source = 'ADF Duplex'

# we want a4
s.pageheight = 297
s.pagewidth = 210
s.br_y = 297
s.br_x = 210
i=0

mem=memory()

c = canvas.canvas()
p = []
for im in s.multi_scan():
    i=i+1
#    (width,height) = im.size
#    print width, height
    c.insert(bitmap.bitmap(0, 0, im, document.paperformat.A4.width, document.paperformat.A4.height, compressmode="DCT",dctquality=30))
    p.append(document.page(c))
d=document.document(p)
d.writePDFfile("test.pdf")
print memory(mem)
s.close()

