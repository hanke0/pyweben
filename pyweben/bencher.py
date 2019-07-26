import os
from functools import partial

from locust import HttpLocust, TaskSet, task
from locust.clients import HttpSession

from pyweben.utils import n_bytes_json
from pyweben.config import load_config


def _http_request(self, url, method):
    c: HttpSession = self.client
    size = os.path.basename(url)
    if method == "POST":
        rsp = c.post(url, json=n_bytes_json(size, dumps=False))
    else:
        rsp = c.get(url, params={'source': 'hhh'})
    rsp.text
    return


def _create_locust_task_set_cls(name, url_iter):
    methods = {}
    for method_name, request in url_iter:
        method, url = request.split(" ", 1)
        method = method.strip().upper()
        url = url.strip()
        methods[method_name] = task(partial(_http_request, url=url, method=method))

    return type(name, (TaskSet, object), methods)


def create_locust(config):
    sections = config.sections()  # type: list
    requests = config['requests']
    rv = {}
    for section in sections:
        if section == 'requests':
            continue
        name = section
        task_set_name = name.title() + "TaskSet"
        locust_name = name.title() + "Locust"
        port = config.getint(section, 'port')
        url_iter = [(k, v.format(port=port, name=name)) for k, v in requests.items()]
        task_set = _create_locust_task_set_cls(task_set_name, url_iter)
        rv[locust_name] = type(locust_name, (HttpLocust, ), {"task_set": task_set})
    return rv


globals().update(create_locust(load_config(os.getenv("PYWEBEN_CONFIG", None))))
