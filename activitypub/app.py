import logging
import os

import tornado.web
from tornado.options import define, options, parse_command_line

from .handlers import (MessageNewHandler, MessageUpdatesHandler,
                       MainHandler, MessageBuffer)

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode", type=bool)
define("directory", default=".", help="location of templates and static", type=str)

class ActivityPubApplocation(tornado.web.Application):
    """
    """
    def __init__(self, *args, **kwargs):
        self.message_buffer = MessageBuffer()
        super().__init__(*args, **kwargs)


def make_app():
    parse_command_line()
    app = ActivityPubApplocation(
        [
            (r"/", MainHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(options.directory), "templates"),
        static_path=os.path.join(os.path.dirname(options.directory), "static"),
        xsrf_cookies=True,
        debug=options.debug,
    )
    return app
    
def main():
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
