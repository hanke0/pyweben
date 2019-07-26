import sanic
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.log import error_logger, access_logger, logger
from pyweben.utils import n_bytes_json, ok_json, setup_log


app = sanic.Sanic("sanic", configure_logging=False)


@app.route('/sanic/<size>', methods=["GET", "POST"])
async def response_bytes(request: Request, size):
    if request.method == "GET":
        request.args.get("source")
        r = HTTPResponse(n_bytes_json(size), content_type="Application/json")
        return r

    data = request.json
    data.get('a')
    r = HTTPResponse(ok_json(), content_type="Application/json")
    return r


def run_sanic(config):
    for log in (error_logger, access_logger, logger):
        setup_log(log, "Sanic")

    port = config['port']
    app.run(host='0.0.0.0', port=int(port), workers=1, access_log=None, )
    return 0
