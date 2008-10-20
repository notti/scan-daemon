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
import BaseHTTPServer, socket, syslog

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head></head><body>blubb<br>")
        s.wfile.write("</body></html>")

class http:
    def __init__(self, config, scanners):
        self.config         = config
        self.scanners       = scanners
        try:
            self.httpd          = BaseHTTPServer.HTTPServer(('',8080), MyHandler)
        except socket.error, (err,message):
            syslog.syslog(syslog.LOG_ERR, message)
            os.exit(1)
        self.httpd.config   = config
        self.httpd.scanners = scanners
    def serve_forever(self):
        self.httpd.serve_forever()

