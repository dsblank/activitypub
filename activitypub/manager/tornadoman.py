try:
    import tornado
    from tornado.web import (Application, RequestHandler)
except:
    pass # tornado not available

import inspect
import jinja2

from .base import Manager, wrap_function, app

def make_handler(f, manager, methods):
    """
    Make a Tornado Handler
    """
    ## TODO: handle GET, POST methods
    class Handler(RequestHandler):
        def get(self):
            return f(self)

        def render_template(self, name, **kwargs):
            self.write(manager.render_template(name, **kwargs))

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
        filters = self.get_filters()
        request = {"args": {}}
        session = {"logged_in": True}
        tornado.log.logging.warning("%s" % filters.keys())
        self.template_env.filters.update(filters)
        template = self.template_env.get_template(name)
        return template.render(config=self.config,
                               request=request,
                               session=session,
                               **kwargs)

    ## TODO: move to app.Data
    #def login_required():
    #    tornado.web.authenticated

    def url_for(self, name):
        return url_for(name)

    @property
    def request(self):
        return request

    def run(self):
        routes = []
        for route, methods, f in app._data.routes:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            routes.append((route, make_handler(f, self, methods)))
        self.app = Application(routes)
        self.app.listen(5000)
        tornado.ioloop.IOLoop.current().start()
