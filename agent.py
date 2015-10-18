import socket
import json
import argparse
import requests

class JSONrequest:
    def __init__(self, **kwargs):
        self.type = type
        self.jsondict = kwargs
    def compile(self):
        return json.dumps(self.jsondict)

def Register(ip, port, name):
    request = JSONrequest(status = "READY", name = name)
    server_result = request.post(request.compile())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--address' type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=8000)
    parser.add_argument('-n', '--name', type=str, default='Node0')
    address =  parser.parse_args().address
    port = parser.parse_args().port


if __name__ = "__main__":
    main()
