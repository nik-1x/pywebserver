from dataclasses import dataclass
import asyncio
import socket
from functools import lru_cache
from .ipmanager import IP, Port
from threading import Thread
import json

class Config:

    def __init__(self, host: IP, port: Port, debug: bool):
        if host.correct:
            self.host = str(host)
        else:
            self.host = '0.0.0.0'

        if port.correct:
            self.port = port.port
        else:
            self.port = 8080

        self.port = port
        self.debug = debug



class Router:

    def __init__(self):
        self.routes = {}
    
    def route(self, path, methods=['GET', 'POST'], cache_func=False, cache_size=256):

        def decorator(func):
            self.routes[path] = {
                'func': func,
                'methods': methods
            }


        if cache_func:
            func = lru_cache(maxsize=cache_size)(decorator)
        else:
            func = decorator

        return func

class RequestEngine:

    def __init__(self):
        pass

    async def parse(self, data) -> dict:

        request_data = data.decode('utf-8').split('\r\n\r\n')
        post_data = request_data[1]
        variables = request_data[0].split('\r\n')

        found = {
            "type": variables[0],
            "headers": {},
            "data": post_data
        }

        for var in variables[1:]:
            if var == '':
                pass
            else:
                try:
                    v = var.split(': ')
                    found["headers"][v[0]] = v[1]
                except Exception as e:
                    pass
        
        return found

    async def contains(self, request, contains_list: list):
        ok = True
        for item in contains_list:
            if item not in request["args"]:
                ok = False
        return ok
    
class ResponseEngine:

    def __init__(self):
        pass

    async def response_builder(self, 
        data: str, 
        status: int = 200, 
        tstatus: str = "OK", 
        headers: dict = {}, 
        content_type: str = "text/html", 
        type: str = "HTTP/1.1"): 

        response = f"{type} {status} {tstatus}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += "Content-Length: " + str(len(data)) + "\r\n"
        for headerkey, headerval in headers:
            response += f"{headerkey}: {headerval}\r\n"
        response += "\r\n"
        response += data
        return response.encode('utf-8')

class Listener:

    def __init__(self, config, router):
        self.config = config
        self.requestengine: RequestEngine = RequestEngine()
        self.responseengine: ResponseEngine = ResponseEngine()
        self.router: Router = router

    async def task(self, serv_sock):
        client_sock, client_addr = serv_sock.accept()
        dat_ = client_sock.recv(1024)
        data = await self.requestengine.parse(dat_)

        if data['type'] == '':
            return
        if self.config.debug == True:
            print(data['type'])

        map = data['type'].split(' ')
        look = map[1].split("?")
        path = look[0]
        args = {}
        if len(look) > 1:
            argsline = look[1].split("&")
            for arg in argsline:
                if "=" in arg:
                    arg = arg.split("=")
                    args[arg[0]] = arg[1]
                else:
                    args[arg] = None
        if path in self.router.routes:
            router = self.router.routes[path]
            data["args"] = args
            if map[0] in router['methods']:
                try:
                    response = await router['func'](data)
                except Exception as e:
                    response = await self.responseengine.response_builder(json.dumps({
                        "error": str(e)
                    }, sort_keys=True, indent=4), content_type="application/json")
                client_sock.send(response)
            else:
                client_sock.send(await self.responseengine.response_builder("Page not found"))
        client_sock.close()

    async def listener(self):
        serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=0)
        serv_sock.bind((self.config.host, int(str(self.config.port))))
        serv_sock.listen(socket.SOMAXCONN)
        while True:
            try:
                await self.task(serv_sock)
            except Exception as e:
                print("Error: ", str(e))
        serv_sock.close()


class App:

    def __init__(self, config: Config, variables: dict = {}):
        self.config = config
        self.router: Router = Router()
        self.Listener = Listener(config, self.router)
        self.render = ResponseEngine()
        self.variables = variables

        local_ip = socket.gethostbyname(socket.gethostname())

        if config.host == '0.0.0.0':
            host = local_ip
        else:
            host = config.host
        print(f"[init] host={host}, port={config.port}")

    def get(self, key: str):
        return self.variables.get(key)

    def run(self, mode: str = "dev"):
        def start():
            asyncio.run(self.Listener.listener())
        if mode == "dev":
            start()
        elif mode == "prod":
            thread = Thread(target=start, daemon=True)
            thread.start()
        else:
            raise Exception("Invalid mode")
