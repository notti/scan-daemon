#!/usr/bin/python

import socket, os, sys
import ConfigParser

parser = ConfigParser.ConfigParser()
parser.read(['scanner.cfg','/etc/scanner.cfg'])

try:
    sock       = parser.get('main', 'socket')
except:
    print """Config error. Need at least a "socket" in the [main] Section!"""
    exit(os.EX_CONFIG)

s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
s.connect(sock)
s.send(sys.argv[1])
