import tornado.web
import json
class JsonHandler(tornado.web.RequestHandler):
    def prepare(self):
        '''Incorporate request JSON into arguments dictionary.'''
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                for k, v in json_data.items():
                    json_data[k] = [v]
                self.request.arguments.pop(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message)
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)
