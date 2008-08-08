import BaseHTTPServer

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head></head><body>blubb<br>")
        s.wfile.write(" ".join(s.server.scanners.keys()))
        s.wfile.write("</body></html>")

class http:
    def __init__(self, config, scanners):
        self.config         = config
        self.scanners       = scanners
        self.httpd          = BaseHTTPServer.HTTPServer(('',8080), MyHandler)
        self.httpd.config   = config
        self.httpd.scanners = scanners
    def serve_forever(self):
        self.httpd.serve_forever()
