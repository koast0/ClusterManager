import socket
import json

class JSONrequest:
    def __init__(self, type):
        self.type = type
        self.jsondict = dict()
    def __init__(self):
        self.type = ''
        self.jsondict = dict()
    def compile():
        self.jsondict["type"] = self.type;
        return json.dumps(self.jsondict)

def Register(conn):
    request = JSONrequest("READY")
    conn.send(request.compile().encode("UTF-8"))

def StartServer(port):
    sock = socket.socket()
    sock.bind(("", port))
    sock.listen(1)
    conn, address = sock.accept()
    Register(conn)


def main():
    StartServer(8000)


if __name__ = "__main__":
    main()
