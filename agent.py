#!/usr/bin/env python3
import socket
import argparse
import time
import subprocess
from random import random
import threading
import ServerRequest
import logging
from urllib.parse import urlparse, urlunparse


def RandomTimeout(time):
    return (time + random()*time)



def ParceInput():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', "--address", type=str, default='http://localhost:8000')
    parser.add_argument('-n', "--name", type=str, default='Node0')
    address = parser.parse_args().address
    url = urlparse(address, scheme = 'http')
    address = urlunparse(url)
    name = parser.parse_args().name
    return (address, name)


class ProcessWorker(threading.Thread):

    def __init__(self, args, global_data):
        threading.Thread.__init__(self)
        self.args = args
        self.global_data = global_data
        self.stop = threading.Event()

    def finish(self):
        print("finishcall")
        self.stop.set()

    def run(self):
        wait = 2
        while True:
            process = StartProc(self.args)
            if (process.returncode == 0):
                ServerRequest.SuccessReport(self.args[1], self.global_data)
                self.finish()
                return 0
            logging.warning("Process " + self.args[1] + " terminated")
            logging.info(" next try in "+str(wait)+" seconds\n")
            ServerRequest.FailReport(self.args[1], self.global_data)
            time.sleep(wait)
            wait *= 2
            if (wait == 16):
                ServerRequest.LastReport(self.args[1], self.global_data)
                logging.warning("Process " + self.args[1] + " is unable to be launched on this Node")
                self.finish()
                break



def StartProc(args):
    try:
        stdout_file = open("stdout_file", 'w')
        stderr_file = open("stderr_file", 'w')
        proc = subprocess.Popen(
            args[0].split(), stdin=subprocess.PIPE, stdout=stdout_file,
            stderr=stderr_file)
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
                t = ProcessWorker(i, global_data)
                processes[i[1]] = t
                t.start()
        for i in processes:
            print(i)
            mark = True
            for j in range(0, len(action['task'])):
                if action['task'][j][1] == i:
                    action['task'][j][1]
                    mark = False
                    break
            if (mark):
                processes[i].finish()
        return 0



class ServerData:

    def __init__(self, ip, name):
        self.ip = ip
        self.name = name


def main():
    logging.basicConfig(filename='agent.log', level=logging.INFO)
    address, name = ParceInput()
    server_data = ServerData(address, name)
    processes = dict()
    action = ServerRequest.Register(server_data)
    while True:
        DoAction(action, processes, server_data)
        print(processes)
        time.sleep(RandomTimeout(30))
        action = ServerRequest.CheckOut(server_data)


if __name__ == "__main__":
    main()
