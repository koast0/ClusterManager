import argparse
import socket
import json
import threading
import queue
from tornado import httpserver, options
import tornado.web
import uuid
import tornado.ioloop
import tornado.web
import logging
import datetime
from SafeShutdown import MakeSaflyShutdown


class Node:

    def __init__(self, hostname, address, process):
        self.hostname = hostname
        self.address = address
        self.process = process
        self.status = 0
        self.id = uuid.uuid4()


class IndexHandler(tornado.web.RequestHandler):

    def initialize(self, config):
        self.config = config

    def post(self):
        # print(self.request.body.decode("utf-8"))
        if self.request.body:
            try:
                json_data = json.loads(self.request.body.decode("utf-8"))
                self.request.arguments.update(json_data)
            except:
                logging.warning("failed with parcing json")
                return
        self.response = dict()
        try:
            name = self.request.arguments['name']
            status = self.request.arguments['status']
        except:
            logging.warning("Some nessesary json object are not available")
            return
        if (status == "READY"):
            for i in self.config:
                if (i.hostname == name and i.status == 0):
                    if not ('task' in self.response):
                        self.response['task'] = [(i.process, str(i.id))]
                    else:
                        self.response['task'].append((i.process, str(i.id)))
                    self.response['action'] = "exec"
                    logging.info("task " + str(i.id) + "started on " + name)
                    i.status = 1
            if not ('task' in self.response):
                self.response['action'] = "wait"

        if (status == "FAIL" or status == "UNABLE_TO_LAUNCH"):
            try:
                proc_id = self.request.arguments['proc_id']
            except:
                logging.warning("Some nessesary json object are not available")
                return
            self.response['action'] = "wait"
            logging.info("Process " + proc_id + " on " + name + " failed\n")
        if (status == "OK"):
            self.response['action'] = "wait"
            logging.info("Node " + name + " checked out")
        output = json.dumps(self.response)
        self.finish(output)


class Application(tornado.web.Application):

    def __init__(self, config):
        self.queue = queue.Queue()
        self.config = config
        handlers = [
            (r"/", IndexHandler, dict(config=self.config)),
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
        logging.warning("Wrong config file")
        exit(1)


def StartTornado(port, config):
    application = Application(config)
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    MakeSaflyShutdown(server)
    tornado.ioloop.IOLoop.instance().start()



def main():
    logging.basicConfig(filename='master.log', level=logging.INFO)
    config = []
    GetConfigData(config)
    StartTornado(8000, config)

if __name__ == "__main__":
    main()
