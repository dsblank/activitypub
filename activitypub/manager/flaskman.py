try:
    from flask import (Flask, Response, abort,
                       jsonify as flask_jsonify,
                       redirect, render_template,
                       request, session, url_for)
    from flask_wtf.csrf import CSRFProtect
    from flask import jsonify
except:
    pass # flask not available

from .base import Manager, wrap_function, app

class FlaskManager(Manager):
    """
    """
    def render_json(self, obj):
        return jsonify(obj) # has correct header type set

    def get_argument(self, name, default_value=None):
        return request.args.get(name, default_value)

    def render_template(self, template_name, **kwargs):
        values = {}
        for f in app.get_context_processors():
            values.update(f(self))
        values.update(kwargs)
        return render_template(template_name, **values)

    def error(self, error_number):
        return self.render_template("%s.html" % error_number), error_number

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
        for path, methods, f, kwargs in app._data.routes:
            ## Add the route:
            self.app.route(path, methods=methods, **kwargs)(wrap_function(self, f))
        ## Add filters:
        for f in app._data.filters:
            ## Add the template filter function:
            self.app.template_filter()(wrap_function(self, f))
        self.app.run(debug=1, port=self.port)

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
