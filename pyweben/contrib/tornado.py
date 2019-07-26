import json

from tornado import web
from tornado.log import access_log, app_log, gen_log

from pyweben.utils import n_bytes_json, setup_log


class MainHandler(web.RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def get(self, size):
        r = n_bytes_json(size)

        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.write(r)

    def post(self, size):
        data = self.json_args

        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.write(json.dumps({"code": 0, 'msg': "OK"}))


app = web.Application([(r"/tornado/(.*)", MainHandler)])


def run_tornado(config):
    for log in (access_log, app_log, gen_log):
        setup_log(log, "Tornado")

    port = int(config['port'])
    server = app.listen(int(port))
    server.start(1)
    return 0
