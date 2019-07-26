import configparser
import re

config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation(),
    strict=True,
    empty_lines_in_values=False,
)
config.SECTCRE = re.compile(r"\[ *(?P<header>[^]]+?) *\]")
config.optionxform = str


default_config = """
[requests]
request20bytes = GET http://localhost:{port}/{name}/20b
request200bytes = GET http://localhost:{port}/{name}/200b
request2kb = GET http://localhost:{port}/{name}/2kb
request20kb = GET http://localhost:{port}/{name}/20kb
request200kb = GET http://localhost:{port}/{name}/200kb
request2m = GET http://loccalhost:{port}/{name}/2m
request20m = GET http://localhost:{port}/{name}/20m
[flask]
port=5050
wsgi-server=uwsgi
runner=pyweben.contrib.flask:run_flask
[tornado]
port=5051
runner=pyweben.contrib.tornado:run_tornado
[sanic]
port=5052
runner=pyweben.contrib.sanic:run_sanic
"""


def load_config(config_file=None):
    if config_file:
        with open(config_file, "rt") as f:
            config.read_file(f)
    else:
        config.read_string(default_config)
    return config
