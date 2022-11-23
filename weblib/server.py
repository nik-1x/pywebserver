from dataclasses import dataclass
import asyncio
import socket
from functools import lru_cache
from .ipmanager import IP, Port
from threading import Thread

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
        data = data.decode('utf-8').split('\r\n')
        found = {
            "type": data[0],
            "headers": {}
        }
        variables = data[1:]
        for var in variables:
            if var == '':
                pass
            else:
                v = var.split(': ')
                found["headers"][v[0]] = v[1]
        if "." in found['headers']['Host']:
            subdomain = ".".join(found["headers"]["Host"].split(':')[0].split('.')[:-1])
            found["subdomain"] = subdomain
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
        data = await self.requestengine.parse(client_sock.recv(1024))
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
                response = await router['func'](data)
                client_sock.send(response)
            else:
                client_sock.send(await self.responseengine.response_builder("Page not found"))
        client_sock.close()

    async def listener(self):
        serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=0)
        serv_sock.bind((self.config.host, int(str(self.config.port))))
        serv_sock.listen(socket.SOMAXCONN)
        while True:
            await self.task(serv_sock)


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
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.Listener.listener())
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

        if mode == "dev":
            start()
        elif mode == "prod":
            thread = Thread(target=start, daemon=True)
            thread.start()
        else:
            raise Exception("Invalid mode")
