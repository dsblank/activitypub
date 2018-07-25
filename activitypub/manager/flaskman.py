try:
    from flask import (Flask, Response, abort,
                       jsonify as flask_jsonify,
                       redirect, render_template,
                       request, session, url_for)
    from flask_wtf.csrf import CSRFProtect
except:
    pass # flask not available

import inspect

from .base import Manager, app

def wrap_method(self, f):
    def function(*args, **kwargs):
        print(f.__name__, "called with:", args, kwargs)
        return f(self, *args, **kwargs)
    function.__name__ = f.__name__
    return function

class FlaskManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        self.app = Flask(__name__,
                         template_folder="/home/dblank/activitypub/apps/blog/templates/",
                         static_folder="/home/dblank/activitypub/apps/blog/static")
        self.app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
        self.csrf = CSRFProtect(self.app)

        #self.app.config["EXPLAIN_TEMPLATE_LOADING"] = True
        self.app.config["ME"] = {"url": "https://example.com",
                                 "icon": {"url": "https://example.com"},
                                 "icon_url": 'https://cs.brynmawr.edu/~dblank/images/doug-sm-orig.jpg',
                                 "summary": "I'm just me."}
        self.app.config["CSS"] = self.CSS
        self.app.config["NAME"] =  "ActivityPub Blog"
        self.app.config["ID"] = "http://localhost:5000"
        ## Add routes:
        for path, methods, f in app._data.routes:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            print(f.__name__, params)
            if len(params) > 0 and params[0] == "self":
                self.app.route(path)(wrap_method(self, f))
            else:
                self.app.route(path)(f)
        ## Add filters:
        for f in app._data.filters:
            params = [x.name for x in inspect.signature(f).parameters.values()]
            print(f.__name__, params)
            if len(params) > 0 and params[0] == "self":
                self.app.template_filter()(wrap_method(self, f))
            else:
                self.app.template_filter()(f)
        self.app.run(debug=1)

    def load_secret_key(self, name):
        key = self._load_secret_key(name)
        self.app.secret_key = key

    def after_request(self, f):
        """
        Decorator
        """
        return self.app.after_request(f)

    def template_filter(self):
        """
        Decorator
        """
        def decorator(f):
            self.app.template_filter()(f)
        return decorator

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login", next=request.url))
            return f(*args, **kwargs)
        return decorated_function
