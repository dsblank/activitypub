try:
    import tornado
    from tornado.web import (Application, RequestHandler)
except:
    pass # tornado not available

import inspect
import jinja2

from .base import Manager, app, wrap_method

def make_handler(f, manager):
    class Handler(RequestHandler):

        def get(self):
            return f(self)

        def render_template(self, name, **kwargs):
            self.write(manager.render_template(name, **kwargs))

        ## redirect is here
    return Handler

class TornadoManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.get_template_folder()))

    def get_filters(self):
        filters = []
        for f in app._data.filters:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            if len(params) > 0 and params[0] == "self":
                filters.append(wrap_method(self, f))
            else:
                filters.append(f)
        filters = {f.__name__: f for f in filters}
        return filters

    def render_template(self, name, **kwargs):
        filters = self.get_filters()
        config = {}
        config["ME"] = {"url": "https://example.com",
                        "icon": {"url": "https://example.com"},
                        "icon_url": 'https://cs.brynmawr.edu/~dblank/images/doug-sm-orig.jpg',
                        "summary": "I'm just me."}
        config["CSS"] = self.CSS
        config["NAME"] =  "ActivityPub Blog"
        config["ID"] = "http://localhost:5000"

        request = {"args": {}}
        session = {"logged_in": True}

        tornado.log.logging.warning("%s" % filters.keys())
        self.template_env.filters.update(filters)
        template = self.template_env.get_template(name)
        return template.render(config=config,
                               request=request,
                               session=session,
                               **kwargs)

    ## TODO: move to app.Data
    #def login_required():
    #    tornado.web.authenticated

    #def render_template(self, template_name, **kwargs):
    #    return render_template(template_name, **kwargs)

    #def redirect(self, url):
    #    return redirect(url)

    def url_for(self, name):
        return url_for(name)

    @property
    def request(self):
        return request

    def run(self):
        routes = []
        for route, methods, f in app._data.routes:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            routes.append((route, make_handler(f, self)))
        self.app = Application(routes)
        self.app.listen(5000)
        tornado.ioloop.IOLoop.current().start()
