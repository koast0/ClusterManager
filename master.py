import argparse
import socket
import json
import threading
import queue
from tornado import httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.web
from jsonhandler import JsonHandler
class Node:
    def __init__(self, hostname, address, process):
        self.hostname = hostname
        self.address = address
        self.process = process

class IndexHandler(JsonHandler):
    def get(self):
        pass

class Application(tornado.web.Application):
    def __init__(self):
        self.queue = queue.Queue()
        handlers = [
            (r"/", IndexHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


def GetConfigData(nodes):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", type=str, default='')
    config_file = parser.parse_args().config
    try:
        config_data = open(config_file).readlines()
        for i in config_data:
            nodes.append(Node(i.split()[0], i.split()[1], i.split()[2:]))
    except:
        print("Wrong config file")
        exit(1)

def StartTornado(port):
    application = Application()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

def main():
    config = []
    GetConfigData(config)
    StartTornado(8000)

if __name__ == "__main__":
    main()
