import logging
import os

import tornado.web
import tornado.log
from tornado.options import define, options, parse_command_line
from passlib.hash import sha256_crypt as crypt

from .handlers import (MessageNewHandler, MessageUpdatesHandler,
                       MainHandler, MessageBuffer, LoginHandler,
                       LogoutHandler)

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode", type=bool)
define("directory", default=".", help="location of templates and static", type=str)

APPLICATION_NAME = "ActivityPub"

### To change the URLs each handler serves, you'll need to edit:
### 1. This code
### 2. The static/chat.js code
### 3. The template/*.html code

class ActivityPubApplication(tornado.web.Application):
    """
    """
    def __init__(self, *args, **kwargs):
        self.message_buffer = MessageBuffer()
        super().__init__(*args, **kwargs)

    def get_user_data(self, getusername):
        return {
            "password": crypt.hash(getusername),
            }

    def handle_messages(self, messages):
        for message in messages:
            tornado.log.logging.info("handle_message: %s", message)
        self.message_buffer.new_messages(messages)

def make_url(path, handler, kwargs=None, name=None):
    #kwargs["options"] = options
    return tornado.web.url(path, handler, kwargs, name)

def make_app():
    parse_command_line()
    if options.debug:
        import tornado.autoreload
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        tornado.log.logging.info("Debug mode...")
        template_directory = os.path.join(options.directory, 'templates')
        tornado.log.logging.info(template_directory)
        for dirpath, dirnames, filenames in os.walk(template_directory):
            for filename in filenames:
                template_filename = os.path.join(dirpath, filename)
                tornado.log.logging.info("   watching: " + os.path.relpath(template_filename))
                tornado.autoreload.watch(template_filename)
    app = ActivityPubApplication(
        [
            make_url(r"/", MainHandler, name="home"),
            make_url(r'/login', LoginHandler, name="login"),
            make_url(r'/logout', LogoutHandler, name="logout"),
            make_url(r"/message/new", MessageNewHandler),
            make_url(r"/message/updates", MessageUpdatesHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url = "/login",
        template_path=os.path.join(os.path.dirname(options.directory), "templates"),
        static_path=os.path.join(os.path.dirname(options.directory), "static"),
        xsrf_cookies=True,
        debug=options.debug,
    )
    return app
    
def main():
    app = make_app()
    app.listen(options.port)
    tornado.log.logging.info("Starting...")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.log.logging.info("Shutting down...")
    tornado.log.logging.info("Stopped.")
