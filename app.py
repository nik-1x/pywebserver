from weblib.server import *
from weblib.ipmanager import *
from weblib.utils import *
import json

app = App(
    config=Config(
        host=IP('0.0.0.0'),
        port=Port(8080),
        debug=False
    ),
    variables={
        'proj_name': 'Python Web Server Example',
        'proj_version': '1.0.0',
        'proj_author': 'Nick (astralyx.dev)'
    }
)

@app.router.route('/dump', ['GET'], cache_func=True, cache_size=128)
async def index(request: dict):
    return await Render.json(request)


@app.router.route('/api/simpleMethod', ['GET'], cache_func=False)
async def createInvoice(request):
    if await RequestEngine().contains(request, ["token", "test_var"]):

        token = request["args"]["token"]
        test_var = request["args"]["test_var"]

        # do stuff

        return await Render.json({
            "status": "success"
        })
    else:
        return await Render.json({
            "error": "Missing arguments"
        })


app.run(mode="dev")

