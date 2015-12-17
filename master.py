#!/usr/bin/env python3
import argparse
import HTML
import socket
import json
import threading
import queue
from time import sleep
from tornado import httpserver, options
from datetime import *
import tornado.web
import uuid
import tornado.ioloop
import tornado.web
import logging
from SafeShutdown import MakeSaflyShutdown
from DatabaseLogic import SQL

def GetDatetimeObj (t):
    return(datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f"))

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

        def AnswerFail(self, status):
            try:
                proc_id = self.arguments['proc_id']
            except:
                logging.warning("Some nessesary json object are not available")
                return
            db.ProcUpdate(name, status, proc_id)
            self.response['action'] = "wait"
            logging.info("Process " + proc_id + " on " + name + " failed\n")

        def AnswerSuccess(self):
            try:
                proc_id = self.arguments['proc_id']
            except:
                logging.warning("Some nessesary json object are not available")
                return
            db.ProcUpdate(name, "SUCCESS", proc_id)
            self.response['action'] = "wait"
            logging.info("Process " + proc_id + " on " + name + " finished with return code 0\n")

        def AnswerOk(self):
            for i in db.GetTasks(name):
                if (i[0] == name):
                    if not ('task' in self.response):
                        self.response['task'] = [(i[1], i[2])]
                    else:
                        self.response['task'].append((i[1], i[2]))
                    self.response['action'] = "exec"
                    print(db.GetProcStatus(i[2]))
                    if (db.GetProcStatus(i[2]) != "FAIL" and db.GetProcStatus(i[2])!= "UNABLE_TO_LAUNCH" and 
                        db.GetProcStatus(i[2]) != "SUCCESS"):
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
            AnswerFail(self, status)

        if (status == "OK"):
            AnswerOk(self)

        if (status == "SUCCESS"):
            AnswerSuccess(self)

        print(self.body)
        print(self.response)
        self.output = json.dumps(self.response)


class IndexHandler(tornado.web.RequestHandler):

    def post(self):
        output_class = IndexPostAnswer(
            self.request.body)
        output_class.Answerer()
        output = output_class.output
        self.finish(output)


class TaskHandler(tornado.web.RequestHandler):
    def get(self):
        data = db.GetAllTasks()
        data = HTML.table(data)
        self.finish(data)


class ProcHandler(tornado.web.RequestHandler):
    def get(self):
        data = db.GetAllProc()
        data = HTML.table(data)
        self.finish(data)

class NodesHandler(tornado.web.RequestHandler):
    def get(self):
        data = db.GetAllNodes()
        data = HTML.table(data)
        self.finish(data)


class Application(tornado.web.Application):

    def __init__(self):
        self.queue = queue.Queue()
        handlers = [
            (r"/", IndexHandler), 
            (r"/tasks", TaskHandler),
            (r"/proc", ProcHandler),
            (r"/nodes", NodesHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def GetConfigData():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', "--config", type=str, default='')
        config_file = parser.parse_args().config
        config_data = open(config_file).readlines()
        db.AddTaskTableIntoDB(config_data) 
    except:
        logging.info("Wrong config file. Starting with old data")

def StartTornado(port, StatusChecker, NodeRemaper):
    application = Application()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    MakeSaflyShutdown(server, db, StatusChecker, NodeRemaper)
    tornado.ioloop.IOLoop.instance().start()

def CheckProcesses():
    data = db.GetAllNodes()
    for i in range(0, len(data)):
        last_visit = GetDatetimeObj(data[i][1])
        now = datetime.now()
        diffrence = timedelta.total_seconds(now - last_visit)
        if (diffrence > 120):
            logging.info("node " + data[i][0]+ " is offline")
            db.ProcNodeUpdate(status="OLD SESSION PROCESS", name = data[i][0])

class StatusChecker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.offline_nodes = set()

    def run(self):
        if self.stop.is_set():
            return 0
        while True:
            data = db.GetAllNodes()
            for i in range(0, len(data)):
                last_visit = GetDatetimeObj(data[i][1])
                now = datetime.now()
                diffrence = timedelta.total_seconds(now - last_visit)
                if (diffrence > 120):
                    db.ProcNodeUpdate(status="UNABLE_TO_LAUNCH", name = data[i][0])
            if self.stop.is_set():
                    return 0
            sleep(10)
    def finish(self):
        self.stop.set()

class NodeRemaper(threading.Thread):           
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.bad_nodes = dict()
        self.node_load = dict()
    def run(self):
        while True:
            if self.stop.is_set():
                    return 0
            data = db.GetAllFailedProc()
            for i in data:
                if not(i[0] in self.bad_nodes):
                    self.bad_nodes[i[0]]= [i[1]]
                else:
                    self.bad_nodes[i[0]].append(i[1])
            proclist = db.GetAllProc()
            nodes = db.GetAllNodes()
            node_load =dict()
            for i in range(0, len(nodes)):
                last_visit = GetDatetimeObj(nodes[i][1])
                now = datetime.now()
                diffrence = timedelta.total_seconds(now - last_visit)
                if diffrence < 120:
                    node_load[nodes[i][0]] = 0;
            for i in proclist:
                if i[1]=="RUNNING" :
                    if (i[0] in node_load):
                        node_load[i[0]] +=1
            values = sorted(node_load.items(), key = lambda i: i[1])
            # values = [(hostname, processes number), ...]
            print (values)
            for i in data:
                # i = (id, hostname)
                current = 0
                while current!=len(values):
                    if i[0] in self.bad_nodes:
                        if not(values[current][0] in self.bad_nodes[i[0]]):
                            db.TaskUpdate(i[0], values[current][0])
                            db.ProcUpdate(values[current][0], "PREPARING TO RUN", i[0])
                            return 0;
                        else: current+=1
                    else:
                        db.TaskUpdate(i[0], values[current][0])
                        db.ProcUpdate(values[current][0], "PREPARING TO RUN", i[0])
                        return 0;
            sleep(10)
    def finish(self):
        self.stop.set()


def main():
    logging.basicConfig(filename='master.log', level=logging.INFO)
    logging.info("Server started")
    db.CreateDB()
    CheckProcesses()
    GetConfigData()
    t = StatusChecker()
    t.start()
    q = NodeRemaper()
    q.start()
    StartTornado(8000, t, q)

db = SQL()

if __name__ == "__main__":
    main()
