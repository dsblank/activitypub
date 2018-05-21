import uuid

import tornado.escape
import tornado.web
import tornado.log
from tornado.concurrent import Future
from tornado import gen
from passlib.hash import sha256_crypt as crypt

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        super().prepare()
        self.json_data = None
        if self.request.headers.get("Content-Type") == "application/json":
            if self.request.body:
                try:
                    self.json_data = tornado.escape.json_decode(self.request.body)
                except ValueError:
                    tornado.log.logging.info("unable to decode JSON data (%s)", self.request.body)

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if isinstance(user, bytes):
            user = user.decode()
        return user

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')
        
    def post(self):
        getusername = self.get_argument("username")
        getpassword = self.get_argument("password")
        user_data = self.application.get_user_data(getusername)
        tornado.log.logging.info("user_data[password]=%s", user_data["password"])
        tornado.log.logging.info("getpassword=%s", getpassword)
        if user_data and user_data["password"] and crypt.verify(getpassword, user_data["password"]):
            self.set_secure_cookie("user", self.get_argument("username"))
            self.redirect(self.get_argument("next", self.reverse_url("home")))
        else:
            self.redirect(self.reverse_url("login"))

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", self.reverse_url("home")))

class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 200

    def wait_for_messages(self, cursor=None):
        # Construct a Future to return to our caller.  This allows
        # wait_for_messages to be yielded from a coroutine even though
        # it is not a coroutine itself.  We will set the result of the
        # Future when results are available.
        result_future = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.cache[-new_count:])
                return result_future
        self.waiters.add(result_future)
        return result_future

    def cancel_wait(self, future):
        self.waiters.remove(future)
        # Set an empty result to unblock any coroutines waiting.
        future.set_result([])

    def new_messages(self, messages):
        tornado.log.logging.info("Sending new message to %r listeners", len(self.waiters))
        for future in self.waiters:
            future.set_result(messages)
        self.waiters = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        #messages = [message for message in self.application.message_buffer.cache
        #            if message.get("to_address", "") == user]
        messages = [message for message in self.application.message_buffer.cache]
        tornado.log.logging.info("messages: %s", messages)
        self.render("index.html", messages=messages, user=user)

class MessageNewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        message = {
            "id": str(uuid.uuid4()),
            "to_address": self.get_argument("to_address"),
            "from_address": self.get_argument("from_address"),
            "message_type": self.get_argument("message_type"),
            "body": self.get_argument("body"),
            "html": "",
        }
        # message["html"] contains itself:
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message, user=user))
        ## Message goes to database:
        self.application.handle_messages([message])
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            ## Sender gets the message back to handle:
            self.write(message)

class MessageUpdatesHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def post(self):
        ## send info to javascript:
        cursor = self.get_argument("cursor", None)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = self.application.message_buffer.wait_for_messages(cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        self.application.message_buffer.cancel_wait(self.future)
