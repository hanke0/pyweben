import json
import random
import string
import re
import sys
import subprocess
import os
import importlib
import logging

from gevent.pywsgi import WSGIServer as GWSGIServer
from gunicorn.glogging import Logger as _Logger


choices = string.ascii_letters + string.digits


def _random_string(n):
    return "".join(random.choice(choices) for _ in range(n))


def _random_mapping(size, kn, vn=None):
    if vn is None:
        vn = kn
    return {_random_string(kn): _random_string(vn) for _ in range(size)}


_UMO = {
    "B": 1,
    'K': 1024,
    "M": 1024 * 1024,
    "G": 1024 * 1024 * 1024,
}
_regex = re.compile(r"^\s*(?P<n>\d+)(?P<umo>[BKMG]?)B?\s*$", re.IGNORECASE)


def _to_bytes(s):
    s = s.upper()
    m = _regex.match(s)
    return int(round(_UMO[m.group('umo') or "B"] * float(m.group('n'))))


def n_bytes_json(n, dumps=True):
    if isinstance(n, str):
        bytes_n = _to_bytes(n)
    else:
        bytes_n = n

    kn = vn = 8
    if bytes_n > 64:
        size = bytes_n // kn
        while size > 1024:
            vn += 2
            size = bytes_n // kn
    else:
        size = 1
        kn = vn = bytes_n // 2

    if not dumps:
        return _random_mapping(size, kn, vn)
    return json.dumps(_random_mapping(size, kn, vn))


def ok_json(dumps=True):
    if dumps:
        return json.dumps({"code": 0, 'msg': "OK"})
    return {"code": 0, 'msg': "OK"}


class Logger(_Logger):
    error_fmt = r" Gunicorn - %(asctime)s [%(process)d] [%(levelname)s] %(message)s"
    datefmt = r"[%Y-%m-%d %H:%M:%S]"

    access_fmt = " Gunicorn - %(message)s"
    syslog_fmt = " [Gunicorn - %(process)d] %(message)s"

    def __init__(self, cfg):
        prefix = os.getenv("PYWEBEN_APP_NAME", "")
        self.error_fmt = prefix + self.error_fmt
        self.access_fmt = prefix + self.error_fmt
        self.syslog_fmt = prefix + self.error_fmt
        super().__init__(cfg)


def run_gunicorn(port, wsgi):
    bind = '0.0.0.0:%s' % port
    cmd = os.path.join(os.path.dirname(sys.executable), 'gunicorn')
    args = [
        cmd, "-b", bind, "-w", "1", "--disable-redirect-access-to-syslog",
        "--log-level", "ERROR", wsgi, "--logger-class", "pyweben.utils.Logger"
    ]
    print("Server:", " ".join(args))
    env = os.environ.copy()
    env['PYWEBEN_APP_NAME'] = wsgi
    code = subprocess.call(args, env=env)
    return code


def run_uwsgi(port, wsgi):
    bind = '0.0.0.0:%s' % port
    cmd = os.path.join(os.path.dirname(sys.executable), 'uwsgi')
    args = [
        cmd, "--http-socket", bind, "-p", "1", "--disable-logging", "-w", wsgi, "--need-app",
        f"--log-prefix={wsgi}-uWSGI", "--master", "--die-on-term",
    ]
    for path in sys.path:
        args.extend(["--python-path", path])

    print("Server:", " ".join(args))
    code = subprocess.call(args, env=os.environ)
    return code


def run_gevent(port, wsgi):
    from gevent.monkey import patch_all
    patch_all()

    def _get_app(p):
        module, app = p.split(':', 1)
        module = importlib.import_module(module)
        return getattr(module, app or "app")

    bind = '0.0.0.0:%s' % port
    app = _get_app(wsgi)
    server = GWSGIServer(bind, app, log=None)
    print("Server: gevent", bind)
    server.serve_forever()
    return 0


def run_wsgi(wsgi_import_path, config):
    port = int(config['port'])
    wsgi = config.get('wsgi-server', 'gunicorn').lower()

    if wsgi == 'gevent':
        return run_gevent(port, wsgi_import_path)

    if wsgi == 'gunicorn':
        return run_gunicorn(port, wsgi_import_path)

    if wsgi == 'uwsgi':
        return run_uwsgi(port, wsgi_import_path)

    raise TypeError(f'Unknown wsgi server: {wsgi}')


def run_locust(file, clients, hatch_rate, run_time, csv_base_name):
    cmd = os.path.join(os.path.dirname(sys.executable), 'locust')
    args = [
        cmd, "-f", file, "--no-web", "--clients", str(clients), '--hatch-rate', str(hatch_rate),
        '--run-time', str(run_time), "--loglevel", "WARNING", "--csv-base-name", csv_base_name,
        '--host', "http://localhost"
    ]
    print("Run locust:", " ".join(args))
    code = subprocess.call(args, env=os.environ)
    return code


def run_locust_web(file):
    cmd = os.path.join(os.path.dirname(sys.executable), 'locust')
    args = [
        cmd, "-f", file, "--loglevel", "WARNING", "--port", "8090", '--host', "http://localhost"
    ]
    print("Run locust:", " ".join(args))
    code = subprocess.call(args, env=os.environ)
    return code


def setup_log(log, name):
    fmt = logging.Formatter(f"{name} - %(asctime)s [%(process)d] [%(levelname)s] %(message)s")
    hdl = logging.StreamHandler()
    hdl.setFormatter(fmt)

    log.handlers.clear()
    log.addHandler(hdl)


if __name__ == '__main__':
    _to_bytes("1kb")
