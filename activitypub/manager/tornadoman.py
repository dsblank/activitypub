try:
    import tornado
    from tornado.web import (Application, RequestHandler)
except:
    pass # tornado not available

import jinja2
import re

from .base import Manager, wrap_function, app
from ..classes import ActivityPubBase

class Container():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def make_handler(f, manager, methods, route, kws):
    """
    Make a Tornado Handler
    """
    ## TODO: handle GET, POST methods
    ## TODO: format args via route types, <int:page>
    ## TODO: handle flask-style keywords in kws:
    #    defaults, strict_slashes, endpoint
    if "endpoint" in kws:
        f.__name__ = kws["endpoint"]
    class Handler(RequestHandler):
        """
        A handler that replicates some of the methods in Manager
        so that developers don't need to know.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._filters = None
            manager.template_env.filters.update(self.get_filters())

        def get_template_namespace(self):
                ns = super().get_template_namespace()
                ns.update({
                    'config': 'John Doe',
                })
                return ns

        def __getattr__(self, attr):
            return getattr(manager, attr)

        def get(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        def get_filters(self):
            if self._filters is None:
                self._filters = {f.__name__: wrap_function(self, f)
                                 for f in app.get_filters()}
            return self._filters

        def _render_template(self, name, **kwargs):
            tornado.log.logging.warning("kwargs: %s" % list(kwargs.keys()))
            values = {
                "request": Container(path=self.request.path,
                                     args={k: self.get_argument(k) for k in self.request.arguments}),
                "session": Container(logged_in=True),
                "config": self.config,
            }
            for f in app.get_context_processors():
                values.update(f(self))
            values.update(kwargs)
            template = manager.template_env.get_template(name)
            tornado.log.logging.warning("values: %s" % list(values.keys()))
            return template.render(**values)

        def render_template(self, name, **kwargs):
            self.write(self._render_template(name, **kwargs))

        def render_json(self, obj):
            self.write(obj) # will set header to JSON mimetype

        def error(self, error_number):
            self.set_status(error_number)
            self.write(manager.render_template("%s.html" % error_number))

        def url_for(self, name):
            return manager.url_for(name)

        #@property
        #def request(self):
        #    return Request("/test", {k: self.get_argument(k) for k in self.request.arguments})

        # Get for free:
        #   * get_argument
        #   * request

    return Handler

class TornadoManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filters = None
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.get_template_folder()))

    def run(self):
        self.config["CSS"] = self.CSS
        routes = []
        for route, methods, f, kwargs in app.get_routes():
            re_route = re.sub("\<[^\>]*\>", r"([^/]*)", route)
            routes.append((re_route, make_handler(f, self, methods, route, kwargs)))
        self.app = Application(routes)
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()
