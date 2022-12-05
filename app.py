from weblib.server import *
from weblib.ipmanager import *
from weblib.utils import *
from weblib.tmanager import *

app = App(
    config=Config(
        host=IP('0.0.0.0'),
        port=Port(8083),
        debug=True
    ),
    variables={
        'proj_name': 'TUQ API',
        'proj_version': '1.0.0',
        'proj_author': 'Nick',
        'host': 'localhost:8083'
    }
)

# host
@app.router.route('/api/auth', ['POST'], cache_func=True, cache_size=256)
async def getAds(request: dict):
    
    return await Render.json({
        'request': request
    })


def tasker():
    print("Working")


NewTask(tasker).start()
app.run(mode="dev")