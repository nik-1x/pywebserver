from weblib.server import *
from weblib.ipmanager import *
from weblib.utils import *
from weblib.tmanager import *

import time

app = App(
    config=Config(
        host=IP('0.0.0.0'),
        port=Port(8083),
        debug=True
    ),
    variables={
        'proj_name': 'TUQ API',
        'proj_version': '1.0.0',
        'proj_author': 'Nick'
    }
)

requests_count = 0

# host
@app.router.route('/api/example', ['POST'], cache_func=True, cache_size=256)
async def getAds(request: dict):

    global requests_count 
    requests_count += 1

    if request['data']:
        return await Render.json({
            'response': request 
        })
    else:
        return await Render.json({
            'error': 'request data is empty'
        })

# requests count cleaner
def requests_count_cleaner():
    global requests_count
    requests_count = 0
    time.sleep(5*60) # every 5 mins


NewTask(requests_count_cleaner).start()
app.run(mode="dev")