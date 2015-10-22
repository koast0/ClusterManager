import socket
import argparse
import time
import subprocess
from random import random
import threading
import ServerRequest
import logging


def RandomTimeout(time):
    return (time + random()*time)



def ParceInput():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', "--address", type=str, default='localhost')
    parser.add_argument('-p', "--port", type=int, default=8000)
    parser.add_argument('-n', "--name", type=str, default='Node0')
    address = parser.parse_args().address
    if address[0:7] != "http://":
        address = "http://" + address
    port = parser.parse_args().port
    name = parser.parse_args().name
    return (address, port, name)


class ProcessWorker(threading.Thread):

    def __init__(self, args, processes, global_data):
        threading.Thread.__init__(self)
        self.args = args
        self.processes = processes
        self.global_data = global_data
        self.stop = threading.Event()

    def run(self):
        wait = 1
        while True:
            process = StartProc(self.args, self.processes)
            logging.warning("Process " + self.args[1] + " terminated")
            logging.info(" next try in "+str(wait)+" seconds\n")
            ServerRequest.FailReport(self.args[1], self.global_data)
            time.sleep(wait)
            wait *= 2
            if (wait == 128):
                ServerRequest.LastReport(self.args[1], self.global_data)
                logging.warning("Process " + self.args[1] + " is unable to be launched on this Node")
                finish()

    def finish(self):
        self.stop.set()


def StartProc(args, working_on):
    try:
        stdout_file = open("stdout_file", 'w')
        stderr_file = open("stderr_file", 'w')
        proc = subprocess.Popen(
            args[0], stdin=subprocess.PIPE, stdout=stdout_file,
            stderr=stderr_file)
        working_on[args[1]] = proc
        proc.wait()
    finally:
        stderr_file.close()
        stdout_file.close()
    return proc


def DoAction(action, processes, global_data):
    if action["action"] == "wait":
        return 0
    if action["action"] == "exec":
        for i in action['task']:
            if not i[1] in processes:
                t = ProcessWorker(i, processes, global_data)
                t.start()
        return 0


class ServerData:

    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name


def main():
    logging.basicConfig(filename='agent.log', level=logging.INFO)
    address, port, name = ParceInput()
    server_data = ServerData(address, port, name)
    processes = dict()
    action = ServerRequest.Register(server_data)
    while True:
        DoAction(action, processes, server_data)
        time.sleep(RandomTimeout(40))
        action = ServerRequest.CheckOut(server_data)


if __name__ == "__main__":
    main()
