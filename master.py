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
from datetime import datetime
from jsonhandler import JsonHandler
class Node:
    def __init__(self, hostname, address, process):
        self.hostname = hostname
        self.address = address
        self.process = process
        self.status = 0;
        self.last_check_in = datetime.max;
class IndexHandler(JsonHandler):
    def get(self, config):
        name = self.request.arguments['name']
        status = self.request.arguments['status']
        if (status == "READY"):
            for i in config:
                if (i.hostname == name and i.address == 
                    self.client_address[0]):
                    self.response['task'] = i.process
            self.write_json()
        if (status == "FAIL"):
            f = open("log.txt", 'w')
            f.write("Process on " + name + " failed\n")
            f.close()
        if (status == "OK"):
            for i in config:
                if (i.hostname == name and i.address == 
                    self.client_address[0]):
                    i.last_check_in = datetime.now().time()


class Application(tornado.web.Application):
    def __init__(self, config):
        self.queue = queue.Queue()
        self.config = config
        handlers = [
            (r"/", IndexHandler, config),
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

def StartTornado(port, config):
    application = Application(config)
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

def main():
    config = []
    GetConfigData(config)
    StartTornado(8000, config)

if __name__ == "__main__":
    main()
