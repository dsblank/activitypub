from flask import (Flask, Response)

from .base import Manager
    
class FlaskManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Flask(__name__)

    def after_request(self, f):
        """
        Decorator
        """
        self.app.after_request(f)

    def template_filter(self):
        """
        Decorator
        """
        def decorator(f):
            self.app.template_filter()(f)
        return decorator
