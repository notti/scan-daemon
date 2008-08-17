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

