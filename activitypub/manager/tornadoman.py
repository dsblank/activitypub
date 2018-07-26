try:
    import tornado
    from tornado.web import (Application, RequestHandler)
except:
    pass # tornado not available

import inspect
import jinja2

from .base import Manager, wrap_function, app
from .._version import VERSION

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
        ## TODO : add context_processor
        q = {
            "type": "Create",
            "activity.object.type": "Note",
            "activity.object.inReplyTo": None,
            "meta.deleted": False,
        }
        notes_count = self.database.activities.find(
            {"box": "outbox", "$or": [q, {"type": "Announce", "meta.undo": False}]}
        ).count()
        q = {"type": "Create", "activity.object.type": "Note", "meta.deleted": False}
        with_replies_count = self.database.activities.find(
            {"box": "outbox", "$or": [q, {"type": "Announce", "meta.undo": False}]}
        ).count()
        liked_count = self.database.activities.count(
            {
                "box": "outbox",
                "meta.deleted": False,
                "meta.undo": False,
                "type": "Like",
            }
        )
        followers_q = {
            "box": "inbox",
            "type": "follow",
            "meta.undo": False,
        }
        following_q = {
            "box": "outbox",
            "type": "follow",
            "meta.undo": False,
        }
        kwargs.update({
            "request":  {"args": {}},
            "session": {"logged_in": True},
            "microblogpub_version": VERSION,
            "followers_count": self.database.activities.count(followers_q),
            "following_count": self.database.activities.count(following_q),
            "notes_count": 0, #notes_count,
            "liked_count": 0, #liked_count,
            "with_replies_count": 0, #with_replies_count,
            "DOMAIN": "localhost:5000/test", # for tornado  TODO: update on each fetch, include full URL, /test
            })
        filters = self.get_filters()
        tornado.log.logging.warning("%s" % list(filters.keys()))
        self.template_env.filters.update(filters)
        template = self.template_env.get_template(name)
        return template.render(config=self.config,
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
        self.config["CSS"] = self.CSS
        routes = []
        for route, methods, f in app._data.routes:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            routes.append((route, make_handler(f, self, methods)))
        self.app = Application(routes)
        self.app.listen(5000)
        tornado.ioloop.IOLoop.current().start()
