import json
import requests


class JSONrequest:

    def __init__(self, **kwargs):
        self.type = type
        self.jsondict = kwargs

    def compile(self):
        return json.dumps(self.jsondict)


def RequestToServer(server_data, json_data):
    ip = server_data.ip
    name = server_data.name
    headers = {"Accept": "application/json"}
    server_result = requests.post(ip, data=json_data.compile(),
                                  headers=headers) 
    return json.loads(server_result.content.decode("utf-8"))


def Register(server_data):
    json_data = JSONrequest(status="READY", name=server_data.name)
    return RequestToServer(server_data, json_data)


def CheckOut(server_data):
    json_data = JSONrequest(status="OK", name=server_data.name)
    return RequestToServer(server_data, json_data)


def FailReport(proc_id, global_data):
    json_data = JSONrequest(
        status="FAIL", name=global_data.name, proc_id=proc_id)
    RequestToServer(global_data, json_data)


def LastReport(proc_id, global_data):
    json_data = JSONrequest(
        status="UNABLE_TO_LAUNCH", name=global_data.name, proc_id=proc_id)
    RequestToServer(global_data, json_data)
