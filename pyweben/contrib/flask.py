import json

import flask

from pyweben.utils import n_bytes_json, run_wsgi


app = flask.Flask('pyweben', static_folder=None, static_url_path=None, template_folder=None)


@app.route("/flask/<size>", methods=["GET", "POST"])
def response_bytes(size):
    if flask.request.method == "GET":
        s = flask.request.args.get('source')
        return flask.Response(n_bytes_json(size), mimetype=app.config["JSONIFY_MIMETYPE"], )
    data = flask.request.json
    data.get('aaa')
    return flask.Response(
        json.dumps({"code": 0, 'msg': "OK"}),
        mimetype=app.config["JSONIFY_MIMETYPE"]
    )


def run_flask(config):
    return run_wsgi(__name__ + ":app", config)
