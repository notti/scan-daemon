#!/usr/bin/python

# Copyright (c) 2008 Gernot Vormayr <notti@fet.at>
#
# This file is part of scan-daemon.
# 
# scan-daemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# scan-daemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
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
