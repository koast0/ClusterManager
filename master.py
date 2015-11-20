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


class IndexPostAnswer:

    def __init__(self, body):
        self.body = body
        self.arguments = dict()
        self.response = dict()
        self.output = ''

    def Answerer(self):

        def AnswerReady(self):
            for i in db.GetTasks(name):
                if (i[0] == name):
                    if not ('task' in self.response):
                        self.response['task'] = [(i[1], i[2])]
                    else:
                        self.response['task'].append((i[1], i[2]))
                    self.response['action'] = "exec"
                    logging.info("task " + i[2] + "started on " + name)
                    db.ProcUpdate(name, "RUNNING", str(i[2]))
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
            for i in db.GetTasks(name):
                if (i[0] == name):
                    if not ('task' in self.response):
                        self.response['task'] = [(i[1], i[2])]
                    else:
                        self.response['task'].append((i[1], i[2]))
                    self.response['action'] = "exec"
                    print(db.GetProcStatus(i[2]))
                    if (db.GetProcStatus(i[2]) != "FAIL" and db.GetProcStatus(i[2])!= "UNABLE_TO_LAUNCH"):
                        db.ProcUpdate(name, "RUNNING", str(i[2]))
            if not ('task' in self.response):
                self.response['action'] = "wait"
            logging.info("Node " + name + " checked out")

        
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
        print(self.body)
        print(self.response)
        self.output = json.dumps(self.response)


class IndexHandler(tornado.web.RequestHandler):

    def initialize(self):
        pass

    def post(self):
        output_class = IndexPostAnswer(
            self.request.body)
        output_class.Answerer()
        output = output_class.output
        self.finish(output)


class Application(tornado.web.Application):

    def __init__(self):
        self.queue = queue.Queue()
        handlers = [
            (r"/", IndexHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


def GetConfigData():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", type=str, default='')
    config_file = parser.parse_args().config
    try:
        config_data = open(config_file).readlines()
        db.AddTaskTableIntoDB(config_data) 
    except:
        logging.info("Wrong config file. Starting with old data")


def StartTornado(port):
    application = Application()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    MakeSaflyShutdown(server)
    tornado.ioloop.IOLoop.instance().start()


def main():
    logging.basicConfig(filename='master.log', level=logging.INFO)
    db.CreateDB()
    GetConfigData()
    StartTornado(8000)

if __name__ == "__main__":
    main()
