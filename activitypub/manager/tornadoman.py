import tornado
from tornado.web import (Application, RequestHandler)

from .base import Manager

class TornadoRoutes():
    routes = []
    def __init__(self, manager):
        self.manager = manager

    def __call__(self, path, methods=["GET"]):
        def decorator(function):
            for method in methods:
                if method == "GET":
                    class TempHandler(RequestHandler):
                        def get(self, manager, *args, **kwargs):
                            function(manager, *args, **kwargs)
                elif method == "POST":
                    class TempHandler(RequestHandler):
                        def post(self, manager, *args, **kwargs):
                            function(manager, *args, **kwargs)
                TornadoRoutes.routes.append((path, TempHandler))
        return decorator

class TornadoManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route = TornadoRoutes()

    def login_required():
        tornado.web.authenticated

    def run(self):
        self.app = Application()
        #super().__init__([url(handler[0],
        #                      handler[1],
        #                      handler[3],
        #                      name=handler[2])
        #                  for handler in handlers], **settings)
        self.app.listen(5005)
        tornado.ioloop.IOLoop.current().start()
