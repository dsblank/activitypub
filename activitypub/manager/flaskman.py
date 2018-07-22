from flask import (Flask, Response, abort,
                   jsonify as flask_jsonify,
                   redirect, render_template,
                   request, session, url_for)

from flask_wtf.csrf import CSRFProtect

from .base import Manager

class FlaskManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Flask(__name__)
        self.app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
        self.csrf = CSRFProtect(app)

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
