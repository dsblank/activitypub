try:
    from flask import (Flask, Response, abort,
                       jsonify as flask_jsonify,
                       redirect, render_template,
                       request, session, url_for)
    from flask_wtf.csrf import CSRFProtect
except:
    pass # flask not available

from .base import Manager, wrap_function, app

class FlaskManager(Manager):
    """
    """
    def render_template(self, template_name, **kwargs):
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
