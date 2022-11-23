from .server import *
from .ipmanager import *
import json

class Render:

    async def json(data: dict):
        return await ResponseEngine().response_builder(
            json.dumps(data, indent=4, sort_keys=True), 
            content_type="application/json"
        )

    async def html(data: str):
        return await ResponseEngine().response_builder(
            data, 
            content_type="text/html"
        )