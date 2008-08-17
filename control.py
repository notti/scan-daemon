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
import socket, os, syslog

class control:
    def __init__(self, config, scanners):
        self.config = config
        self.scanners = scanners
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            try:
                os.remove(config.socket)
            except OSError:
                pass
            self.socket.bind(config.socket)
        except socket.error, err:
            syslog.syslog(syslog.LOG_ERR, err)
            os.exit(1)

    def serve_forever(self):
        while True:
            command = self.socket.recv(1024).split(' ')
            if len(command) == 2:
                self.scanners.status_change(command[0], command[1])
            if len(command) == 1:
                if command[0]=='shutdown':
                    self.scanners.shutdown()

