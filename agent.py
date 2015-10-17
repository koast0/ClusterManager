import socket
import json
import argparse

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--address' type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=8888)
    address =  parser.parse_args().address
    port = parser.parse_args().port


if __name__ = "__main__":
    main()
