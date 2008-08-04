import socket, os

class control:
    def __init__(self, config, scanners):
        self.config = config
        self.scanners = scanners
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            os.remove(config.socket)
        except OSError:
            pass
        self.socket.bind(config.socket)

    def serve_forever(self):
        while True:
            try:
                scanner, status = self.socket.recv(1024).split(' ')
                print scanner, status
                self.scanners[scanner].status_change(status)
            except:
                pass

