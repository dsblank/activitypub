from .base import Manager

class TornadoManager(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.app = Flask(__name__)
