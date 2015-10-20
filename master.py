import argparse
import socket
import json
import threading
import queue
from tornado import httpserver
import tornado.web
import tornado.ioloop
import tornado.web
from datetime import datetime


class Node:

    def __init__(self, hostname, address, process):
        self.hostname = hostname
        self.address = address
        self.process = process
        self.status = 0
        self.last_check_in = datetime.max


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config=config

    def post(self):
        # print(self.request.body.decode("utf-8"))
        if self.request.body:
            try:
                json_data = json.loads(self.request.body.decode("utf-8"))
                self.request.arguments.update(json_data)
            except:
                print("failed with parcing json")
                return
        self.response = dict()
        try:
            name = self.request.arguments['name']
            status = self.request.arguments['status']
        except:
            print("Some nessesary json object are not available")
            return
        if (status == "READY"):
            for i in self.config:
                if (i.hostname == name && status = 0):
                    if not ('task' in self.response):
                        self.response['task'] =  [i.process]
                    else:
                        self.response['task'].append(i.process)
                    self.response['action'] = "exec"
                    status = 1;
            if not ('task' in self.response):
                self.response[action] = "wait"

        if (status == "FAIL"):
            f = open("log.txt", 'a')
            f.write("Process on " + name + " failed\n")
            f.close()
        if (status == "OK"):
            for i in self.config:
                if (i.hostname == name and i.address ==
                        self.client_address[0]):
                    i.last_check_in = datetime.now().time()
        output = json.dumps(self.response)
        self.finish(output)



class Application(tornado.web.Application):

    def __init__(self, config):
        self.queue = queue.Queue()
        self.config = config
        handlers = [
            (r"/", IndexHandler, dict(config = self.config)),
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

def LogFile():
    f = open("log.txt", 'w')
    f.close()
def main():
    config = []
    LogFile()
    GetConfigData(config)
    StartTornado(8000, config)

if __name__ == "__main__":
    main()
