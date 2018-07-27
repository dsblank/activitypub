try:
    import tornado
    from tornado.web import (Application, RequestHandler)
except:
    pass # tornado not available

import jinja2
import re

from .base import Manager, wrap_function, app
from ..classes import ActivityPubBase

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
        def get(self, *args, **kwargs):
            self.database = manager.database
            for name in ActivityPubBase.CLASSES:
                setattr(self, name, getattr(manager, name))
            return f(self, *args, **kwargs)

        def render_template(self, name, **kwargs):
            self.write(manager.render_template(name, **kwargs))

        def render_json(self, obj):
            self.write(obj) # will set header to JSON mimetype

        def error(self, error_number):
            self.set_status(error_number)
            self.write(manager.render_template("%s.html" % error_number))

        def url_for(self, name):
            return manager.url_for(name)

        # Get for free:
        #   * get_argument

    return Handler

class TornadoManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filters = None
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.get_template_folder()))

    def get_filters(self):
        if self._filters is None:
            self._filters = {f.__name__: wrap_function(self, f)
                             for f in app._data.filters}
        return self._filters

    def render_template(self, name, **kwargs):
        values = {}
        for f in app.get_context_processors():
            values.update(f(self))
        values.update(kwargs)
        filters = self.get_filters()
        tornado.log.logging.warning("%s" % list(filters.keys()))
        self.template_env.filters.update(filters)
        template = self.template_env.get_template(name)
        return template.render(config=self.config, **values)

    ## TODO: move to app.Data
    #def login_required():
    #    tornado.web.authenticated

    @property
    def request(self):
        return request

    def run(self):
        self.config["CSS"] = self.CSS
        routes = []
        for route, methods, f, kwargs in app._data.routes:
            re_route = re.sub("\<[^\>]*\>", r"([^/]*)", route)
            routes.append((re_route, make_handler(f, self, methods, route, kwargs)))
        self.app = Application(routes)
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()
