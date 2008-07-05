s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    os.remove("/tmp/socketname")
except OSError:
    pass
s.bind("/tmp/socketname")
s.listen(1)
conn, addr = s.accept()
SO_PEERCRED = 17

pid, uid, gid = struct.unpack('3i', sock.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize('3i')))
