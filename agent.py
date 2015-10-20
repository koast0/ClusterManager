import socket
import json
import argparse
import requests
import time
import subprocess

class JSONrequest:

    def __init__(self, **kwargs):
        self.type = type
        self.jsondict = kwargs

    def compile(self):
        return json.dumps(self.jsondict)


def Register(ip, port, name):
    data = JSONrequest(status="READY", name=name)
    print (data.compile())
    headers = {"Accept": "application/json"}
#print ('@@@@@@@@@@@@@@@@@@@@@@@',json.loads(request.compile()))
    print(ip+':'+str(port))
    server_result = requests.post(ip+':'+str(port)+'/', data=data.compile(),
                    headers = headers)
    print (server_result.content)
    return json.loads(server_result.text.decode("utf-8"))


def ParceInput(address, port, name):
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
def StartProc(args, working_on):
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=stdout_file, stderr=stderr_file,
                            universal_newlines=True)

    working_on.append(proc)
def DoAction(action):
    if action["action"] = "wait":
        return 0
    if action["action"] = "exec":
        for i in action[task]:
            StartProc(i)
            return 0



def main():
    port = 0
    address = ''
    name = ''
    address, port, name = ParceInput(address, port, name)
    while True:
        action = Register(address, port, name)
        DoAction(action)
        time.sleep(60)

if __name__ == "__main__":
    main()
