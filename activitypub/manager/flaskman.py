try:
    from flask import (Flask, Response, abort,
                       jsonify as flask_jsonify,
                       redirect, render_template,
                       request, session, url_for)
    from flask_wtf.csrf import CSRFProtect
except:
    pass # flask not available

from .base import Manager, wrap_function, app
from .._version import VERSION

class FlaskManager(Manager):
    """
    """
    def render_template(self, template_name, **kwargs):
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
        return render_template(template_name, **kwargs)

    def redirect(self, url):
        return redirect(url)

    def url_for(self, name):
        return url_for(name)

    @property
    def request(self):
        return request

    def run(self):
        self.app = Flask(__name__,
                         template_folder=self.get_template_folder(),
                         static_folder=self.get_static_folder())
        self.app.config.update(WTF_CSRF_CHECK_DEFAULT=False)
        self.app.config["CSS"] = self.CSS
        self.app.config.update(self.config)
        self.csrf = CSRFProtect(self.app)
        ## Add routes:
        for path, methods, f in app._data.routes:
            ## Add the route:
            self.app.route(path, methods=methods)(wrap_function(self, f))
        ## Add filters:
        for f in app._data.filters:
            ## Add the template filter function:
            self.app.template_filter()(wrap_function(self, f))
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
