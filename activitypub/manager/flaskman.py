from flask import (Flask, Response, abort,
                   jsonify as flask_jsonify,
                   redirect, render_template,
                   request, session, url_for)
from flask_wtf.csrf import CSRFProtect

from .base import Manager

class FlaskRoutes():
    def __init__(self, manager):
        self.manager = manager

    def __call__(self, path, methods=["GET"]):
        print("Calling FlaskRoutes() with path=", path)
        def decorator(function):
            print("wrapping!")
            @self.manager.app.route(path)
            def f(*args, **kwargs):
                print("calling wrapped function!")
                function(*args, **kwargs)
            print("returning")
        return decorator

class FlaskManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Flask(__name__)
        self.app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
        self.csrf = CSRFProtect(self.app)
        print("here!")
        self.route = FlaskRoutes(self)

    def run(self):
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
