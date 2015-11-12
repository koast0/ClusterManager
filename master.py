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
from SafeShutdown import MakeSaflyShutdown
import DatabaseLogic as db


class Node:

    def __init__(self, hostname, process):
        self.hostname = hostname
        self.process = process
        self.status = 0
        self.id = uuid.uuid4()


class IndexPostAnswer:

    def __init__(self, body, config, nodes):
        self.body = body
        self.arguments = dict()
        self.response = dict()
        self.config = config
        self.nodes = nodes
        self.output = ''

    def Answerer(self):

        def AnswerReady(self):
            for i in self.config:
                if (i.hostname == name and i.status == 0):
                    if not ('task' in self.response):
                        self.response['task'] = [(i.process, str(i.id))]
                    else:
                        self.response['task'].append((i.process, str(i.id)))
                    self.response['action'] = "exec"
                    logging.info("task " + str(i.id) + "started on " + name)
                    db.ProcUpdate(name, "RUNNING", str(i.id))
                    i.status = 1
            if not ('task' in self.response):
                self.response['action'] = "wait"

        def AnswerFail(self):
            try:
                proc_id = self.arguments['proc_id']
            except:
                logging.warning("Some nessesary json object are not available")
                return
            db.ProcUpdate(name, "FAIL", proc_id)
            self.response['action'] = "wait"
            logging.info("Process " + proc_id + " on " + name + " failed\n")

        def AnswerOk(self):
            self.response['action'] = "wait"
            logging.info("Node " + name + " checked out")

        print(self.body)
        if self.body:
            try:
                json_data = json.loads(self.body.decode("utf-8"))
                self.arguments.update(json_data)
            except:
                logging.warning("failed with parcing json")
                return
        try:
            name = self.arguments['name']
            status = self.arguments['status']
        except:
            logging.warning("Some nessesary json object are not available")
            return

        db.NodeUpdate(name)

        if (status == "READY"):
            AnswerReady(self)

        if (status == "FAIL" or status == "UNABLE_TO_LAUNCH"):
            AnswerFail(self)

        if (status == "OK"):
            AnswerOk(self)

        self.output = json.dumps(self.response)


class IndexHandler(tornado.web.RequestHandler):

    def initialize(self, config, nodes):
        self.config = config
        self.nodes = nodes

    def post(self):
        output_class = IndexPostAnswer(
            self.request.body, self.config, self.nodes)
        output_class.Answerer()
        output = output_class.output
        self.finish(output)


class Application(tornado.web.Application):

    def __init__(self, config, nodes):
        self.queue = queue.Queue()
        self.config = config
        self.nodes = nodes
        handlers = [
            (r"/", IndexHandler, dict(config=self.config, nodes=self.nodes)),
        ]
        tornado.web.Application.__init__(self, handlers)


def GetConfigData(nodes):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", type=str, default='')
    config_file = parser.parse_args().config
    try:
        config_data = open(config_file).readlines()
        for i in config_data:
            nodes.append(Node(i.split()[0], i.split()[1:]))
    except:
        logging.warning("Wrong config file")
        exit(1)


def StartTornado(port, config, nodes):
    application = Application(config, nodes)
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    MakeSaflyShutdown(server)
    tornado.ioloop.IOLoop.instance().start()


def main():
    logging.basicConfig(filename='master.log', level=logging.INFO)
    db.CreateDB()
    config = []
    nodes = dict()
    GetConfigData(config)
    StartTornado(8000, config, nodes)

if __name__ == "__main__":
    main()
