import datetime
import inspect
import binascii
import copy
import os
import uuid

class Data():
    routes = []
    filters = []
    context_processors = []

    def clear(self):
        self.routes.clear()
        self.filters.clear()
        self.context_processors.clear()

class Application():
    """
    Instance for saving routes, filters, etc. for app.

    >>> app.clear()
    >>> @app.filter
    ... def upper(item):
    ...     return item.upper()
    >>> len(app._data.filters) == 1
    True
    >>> app._data.filters[0]("testing")
    'TESTING'
    >>> class Test():
    ...     @app.route("/test")
    ...     def route_test(self, *args, **kwargs):
    ...         print(args, kwargs)
    ...         return 42
    >>> t = Test()
    >>> len(app._data.routes) == 1
    True
    >>> path, methods, function, kwargs = app._data.routes[0]
    >>> function(t, 1, 2, 3, hello="world")
    (1, 2, 3) {'hello': 'world'}
    42
    """
    _data = Data()

    def clear(self):
        self._data.clear()

    def filter(self, f):
        """
        Wrap a plain function/method to provide template function.
        """
        self._data.filters.append(f)
        return f

    def route(self, path, methods=None, **kwargs):
        """
        Wrap a function/method as a route.
        """
        methods = ["GET"] if methods is None else methods
        def decorator(f):
            self._data.routes.append((path, methods, f, kwargs))
            return f
        return decorator

    def context_processor(self, f):
        """
        Wrap a plain function/method to provide context processor function.
        """
        self._data.context_processors.append(f)
        return f

    def get_routes(self):
        return self._data.routes

    def get_filters(self):
        return self._data.filters

    def get_context_processors(self):
        return self._data.context_processors

def wrap_function(manager, f):
    """
    General Function/Method Wrapper
    """
    ## Check the signature:
    params = [x.name for x in inspect.signature(f).parameters.values()]
    if len(params) == 0 or params[0] != "self":
        raise Exception("function %s needs 'self' as first parameter"
                        % f.__name__)
    def function(*args, **kwargs):
        results = f(manager, *args, **kwargs)
        return results
    function.__name__ = f.__name__
    return function

class Manager():
    """
    Manager class that ties together ActivityPub objects, defaults,
    and a database.

    >>> from activitypub.database import ListDatabase
    >>> db = ListDatabase()
    >>> manager = Manager(database=db)

    >>> note = manager.Note(
    ...         **{'sensitive': False,
    ...            'attributedTo': 'http://localhost:5000',
    ...            'cc': ['http://localhost:5005/followers'],
    ...            'to': ['https://www.w3.org/ns/activitystreams#Public'],
    ...            'content': '<p>$source.content</p>',
    ...            'tag': [],
    ...            'source': {'mediaType': 'text/markdown', 'content': '$temp_text'},
    ...            'published': '$NOW',
    ...            'temp_uuid': "$UUID",
    ...            'temp_text': 'Hello',
    ...            'id': 'http://localhost:5005/outbox/$temp_uuid/activity',
    ...            'url': 'http://localhost:5005/note/$temp_uuid'
    ...         })
    >>> note.content == '<p>Hello</p>'
    True
    >>> note.source == {'mediaType': 'text/markdown', 'content': 'Hello'}
    True
    >>> "$temp_uuid" not in note.id
    True
    >>> "$temp_uuid" not in note.url
    True
    >>> hasattr(note, "ap_temp_text")
    False
    >>> hasattr(note, "ap_temp_uuid")
    False
    """
    app_name = "activitypub"
    version = "1.0.0"
    key_path = "./keys"

    def __init__(self, context=None, defaults=None, database=None,
                 host="localhost", port=5000):
        from ..classes import ActivityPubBase
        self.port = port
        self.host = host
        ## Put dependent ones first:
        self.defaults = {
            "$DOMAIN": "$SCHEME://$HOST:$PORT",
            "$SCHEME": "http",
            "$HOST": self.host,
            "$PORT": self.port,
            "$UUID4": lambda: str(uuid.uuid4()),
            "$UUID": lambda: binascii.hexlify(os.urandom(8)).decode("utf-8"),
            "$NOW": lambda: (datetime.datetime.utcnow()
                             .replace(microsecond=0).isoformat() + "Z"),
            }
        self.defaults.update(copy.deepcopy(defaults) or self.make_defaults())
        self.callback = lambda box, activity_id: None
        self.context = context
        self.database = database
        self.config = {}
        self.CSS = ""
        self._static_folder = os.path.abspath("./static")
        self._template_folder = os.path.abspath("./templates")
        self._sass_folder = os.path.abspath("./sass")

        def set_port(self, value):
            self._port = value
            self.defaults["$PORT"] = value

        def get_port(self):
            return self._port

        port = property(get_port, set_port)

        def set_host(self, value):
            self._host = value
            self.defaults["$HOST"] = value

        def get_host(self):
            return self._host

        host = property(get_host, set_host)

        def make_wrapper(manager, class_):
            def wrapper(*args, **kwargs):
                return ActivityPubBase.CLASSES[class_](manager, *args, **kwargs)
            return wrapper

        for class_ in ActivityPubBase.CLASSES:
            setattr(self, class_, make_wrapper(self, class_))

    def run(self):
        print("This manager has these filters:")
        print("    %s" % [f.__name__ for f in app.get_filters()])
        print("This manager has these routes:")
        for (route, methods, f, kwargs) in app.get_routes():
            print("    %s %s mapped to %s" % (route, methods, f.__name__))

    def render_template(self, template_name, **kwargs):
        pass

    def render_json(self, json_object):
        pass

    def redirect(self, url):
        pass

    def url_for(self, name):
        ## admin_notifications
        for (route, methods, f, kwargs) in app.get_routes():
            if f.__name__ == name:
                return route
        return None

    def error(self, error_number):
        pass

    @property
    def request(self):
        return None

    def setup_css(self, folder="."):
        import sass
        THEME_STYLE = "light"
        THEME_COLOR = "#1d781d"
        SASS_DIR = os.path.join(os.path.abspath(folder),
                                self.get_sass_folder())
        theme_css = f"$primary-color: {THEME_COLOR};\n"
        with open(os.path.join(SASS_DIR, f"{THEME_STYLE}.scss")) as f:
            theme_css += f.read()
            theme_css += "\n"
        with open(os.path.join(SASS_DIR, "base_theme.scss")) as f:
            raw_css = theme_css + f.read()
            self.CSS = sass.compile(string=raw_css, output_style="compressed")

    def make_defaults(self):
        """
        A default field can refer to itself, which means that it needs a
        value to begin with.

        >>> m = Manager()
        >>> n = m.Note(attributedTo="alyssa", id="23")
        >>> n.to_dict()
        {'@context': 'https://www.w3.org/ns/activitystreams', 'attributedTo': 'alyssa', 'id': '23', 'type': 'Note'}

        A default can be a $-variable, or the name of a "Class.field_name".
        """
        ## Put dependent ones first:
        return {
            "Person.id": "$DOMAIN/$id",
            "Person.likes": "$id/likes",
            "Person.following": "$id/following",
            "Person.followers": "$id/followers",
            "Person.liked": "$id/liked",
            "Person.inbox": "$id/inbox",
            "Person.outbox": "$id/outbox",
            "Person.url": "$id",
        }

    def user_agent(self):
        return "%s (%s/%s; +%s)" % (requests.utils.default_user_agent(),
                                    self.app_name,
                                    self.version,
                                    self.expand_defaults("$SCHEME/$HOST"))

    def expand_defaults(self, string, obj=None):
        """
        Expand a string with defaults.

        >>> m = Manager()
        >>> m.defaults = {"$TEST": "hello",
        ...               "Note.id": {"key1": "xxx"},
        ... }
        >>> m.expand_defaults("$TEST")
        'hello'
        >>> m.expand_defaults("<p>$TEST</p>")
        '<p>hello</p>'
        >>> n = m.Note(attributedTo="test")
        >>> n.ap_id == {"key1": "xxx"}
        True
        """
        for key in self.defaults:
            if key.startswith("$"):
                if key in string:
                    if callable(self.defaults[key]):
                        string = string.replace(key, str(self.defaults[key]()))
                    else:
                        string = string.replace(key, str(self.defaults[key]))
        if obj:
            for key in self.parse(string):
                if key.startswith("$"):
                    if key in string:
                        if hasattr(obj, "ap_" + key[1:]):
                            val = getattr(obj, "ap_" + key[1:])
                        elif "." in key:
                            val = self.get_item_from_dotted("ap_" + key[1:], obj)
                        else:
                            raise Exception("expansion requires %s" % key[1:])
                        if string == key:
                            string = val
                        else:
                            string = string.replace(key, str(val))
        return string

    def topological_sort(self, data):
        """

        >>> manager = Manager()
        >>> manager.Person(id="alyssa").to_dict()
        {'@context': 'https://www.w3.org/ns/activitystreams', 'endpoints': {}, 'followers': 'http://localhost:5000/alyssa/followers', 'following': 'http://localhost:5000/alyssa/following', 'id': 'http://localhost:5000/alyssa', 'inbox': 'http://localhost:5000/alyssa/inbox', 'liked': 'http://localhost:5000/alyssa/liked', 'likes': 'http://localhost:5000/alyssa/likes', 'outbox': 'http://localhost:5000/alyssa/outbox', 'type': 'Person', 'url': 'http://localhost:5000/alyssa'}
        """
        from functools import reduce
        # Find all items that don't depend on anything:
        extra_items_in_deps = reduce(set.union, data.values(), set()) - set(data.keys())
        # Add empty dependences where needed:
        data.update({item: set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.items() if not dep)
            if not ordered:
                break
            for item in ordered:
                yield item
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                    if item not in ordered}

    def build_dependencies_from_item(self, item, s):
        """
        Given {"val": "$x"} return set("x")
        s is a set, returns s with dependencies.

        >>> m = Manager()
        >>> n = m.Note(attributedTo="test")
        >>> m.build_dependencies_from_item({"val": "$x"}, set())
        {'x'}
        >>> m.build_dependencies_from_item({"key1": {"val": "$x"}}, set())
        {'x'}
        >>> s = m.build_dependencies_from_item({"key1": {"val": "$x"},
        ...                                     "key2": {"key3": "$y"}}, set())
        >>> "x" in s
        True
        >>> "y" in s
        True
        >>> len(s)
        2
        """
        if isinstance(item, str):
            for word in self.parse(item):
                if word.startswith("$"):
                    s.add(word[1:])
        elif isinstance(item, dict):
            for key in item:
                self.build_dependencies_from_item(item[key], s)
        elif isinstance(item, list):
            for key in item:
                self.build_dependencies_from_item(key, s)
        return s

    def replace_in_item(self, item, obj):
        """
        Replace the "$x" in {"val": "$x"} with self.ap_x

        >>> manager = Manager()
        >>> n = manager.Note(attributedTo="test")
        >>> n.ap_x = 41
        >>> n.ap_y = 43
        >>> dictionary = {"key1": {"val": "$x"},
        ...               "key2": {"key3": "$y"}}
        >>> retval = manager.replace_in_item(dictionary, n)
        >>> dictionary
        {'key1': {'val': 41}, 'key2': {'key3': 43}}
        """
        if isinstance(item, (bool, int, float)):
            return item
        elif isinstance(item, str):
            return self.expand_defaults(item, obj)
        elif isinstance(item, dict):
            for key in item:
                item[key] = self.replace_in_item(item[key], obj)
            return item
        elif isinstance(item, list):
            for i in range(len(item)):
                item[i] = self.replace_in_item(item[i], obj)
            return item
        else:
            raise Exception("unknown item: %s" % item)

    def get_item_from_dotted(self, dotted_word, obj):
        """
        Get dictionary item from a dotted-word.

        >>> m = Manager()
        >>> n = m.Note(attributedTo="test")
        >>> n.key1 = {"key2": {"key3": 42}}
        >>> m.get_item_from_dotted("key1.key2.key3", n)
        42
        >>> n.ap_key4 = {"key5": {"key6": 43}}
        >>> m.get_item_from_dotted("key4.key5.key6", n)
        43
        """
        current = {key: getattr(obj, key) for key in dir(obj)}
        for word in dotted_word.split("."):
            if "ap_" + word in current:
                current = current["ap_" + word]
            elif word in current:
                current = current[word]
            else:
                return None
        return current

    def fill_in_deep_defaults(self, obj):
        dependencies = self.build_dependencies(obj)
        ## Now, replace them in order:
        for attr_name in self.topological_sort(dependencies):
            if "$" + attr_name in self.defaults:
                attr = self.defaults["$" + attr_name]
            else:
                if hasattr(obj, "ap_" + attr_name):
                    attr = getattr(obj, "ap_" + attr_name)
                elif "." in attr_name:
                    attr = self.get_item_from_dotted(attr_name, obj)
                else:
                    raise Exception("unknown variable: %s" % attr_name)
            if callable(attr):
                attr = attr()
            if attr is None:
                raise Exception("variable depends on field that is empty: %s" % attr_name)
            if isinstance(attr, str) and "$" in attr:
                setattr(obj, attr_name, self.expand_defaults(attr, obj))
            elif isinstance(attr, (dict, list)):
                ## traverse dict recursively, looking for replacements:
                self.replace_in_item(attr, obj)

    def fill_in_defaults(self, obj):
        # Next, fill in field-defaults:
        for key in self.defaults:
            # Person.id
            if isinstance(obj.ap_type, str) and key.startswith(obj.ap_type + "."):
                attr = self.defaults[key]
                if callable(attr):
                    attr = attr()
                attr_name = "ap_" + key[len(obj.ap_type + "."):]
                if getattr(obj, attr_name) is None:
                    setattr(obj, attr_name, attr)
                elif isinstance(attr, str) and "$" + attr_name[3:] in attr:
                    ## recursive:
                    setattr(obj, attr_name,
                            attr.replace("$" + attr_name[3:], getattr(obj, attr_name)))

    def build_dependencies(self, obj):
        """
        Build a dict of name -> set of dependencies.
        Returns a dict: {"id": set("SCHEME", "DOMAIN"), ...}
        """
        dependencies = {}
        for attr_name in dir(obj):
            if attr_name.startswith("ap_"):
                attr = getattr(obj, attr_name)
                if isinstance(attr, str) and "$" in attr:
                    parsed = self.parse(attr)
                    dependencies[attr_name[3:]] = {x[1:].split(".")[0] for x in parsed
                                                   if x.startswith("$") and x[1:] != attr_name[3:]}
                elif isinstance(attr, dict):
                    deps = self.build_dependencies_from_item(attr, set())
                    for item in deps:
                        dependencies[attr_name[3:]] = dependencies.get(attr_name[3:], set())
                        dependencies[attr_name[3:]].add(item)
        return dependencies

    def parse(self, string):
        """
        Parse a string delimited by non-alphanum, non-$/_ symbols.

        >>> from activitypub.manager import Manager
        >>> m = Manager()
        >>> m.parse("apple/banana/$variable")
        ['apple', 'banana', '$variable']
        """
        retval = []
        current = []
        for s in string:
            if (s.isalnum() or s in "_.") or (s in ["$"] and len(current) == 0):
                current.append(s)
            else:
                if current:
                    retval.append("".join(current))
                    if s == "$":
                        current = ["$"]
                    else:
                        current = []
        if current:
            retval.append("".join(current))
        return retval

    def from_dict(self, data):
        from ..classes import ActivityPubBase
        return ActivityPubBase.from_dict(data)

    def to_list(self, item):
        if isinstance(item, list):
            return item
        return [item]

    def on_post_to_box(self, box, activity):
        """
        manager.on_post_to_box("inbox", activity)
        manager.on_post_to_box("outbox", activity)
        manager.on_post_to_box("replies", reply)
        """
        self.database.activities.insert_one(
            {
                "box": box,
                "activity": activity.to_dict(),
                "type": self.to_list(activity.type),
                "remote_id": activity.id,
                "meta": {
                    "undo": False,
                    "deleted": False
                },
            }
        )
        self.callback(box, activity.id)

    def delete_reply(self, actor, note):
        if note.inReplyTo:
            self.database.activities.update_one(
                {"activity.object.id": note.inReplyTo},
                {"$inc": {"meta.count_reply": -1, "meta.count_direct_reply": -1}},
            )

    def set_callback(self, callback):
        self.callback = callback

    def get_followers(self, remote_id):
        q = {
            "remote_id": remote_id,
            "box": "inbox",
            "type": "follow",
            "meta.undo": False,
        }
        return [doc["activity"]["actor"]
                for doc in self.database.activities.find(q)]

    def get_following(self, remote_id):
        q = {
            "remote_id": remote_id,
            "box": "outbox",
            "type": "follow",
            "meta.undo": False,
        }
        return [doc["activity"]["object"]
                for doc in self.database.activities.find(q)]

    def get_iri(self, iri):
        if iri.startswith(self.expand_defaults("$SCHEME/$HOST")):
            ## get from table
            ## self.database.activity.find()
            ## TODO: WIP
            pass
        else:
            try:
                response = requests.get(
                    iri,
                    headers={
                        "User-Agent": self.user_agent(),
                        "Accept": "application/activity+json",
                    },
                    timeout=10,
                    allow_redirects=False,
                    **kwargs)
            except:
                raise Exception("unable to fetch uri")
            return self.handle(response)

    def handle_response(self, response):
        if response.status_code == 404:
            raise Exception("iri is not found")
        elif response.status_code == 410:
            raise Exception("iri is gone")
        elif response.status_code in [500, 502, 503]:
            raise Exception("unable to fetch; server error")
        response.raise_for_status()
        return response.json()

    def load_secret_key(self, name):
        key = self._load_secret_key(name)
        ## Override to do something with secret key

    def _load_secret_key(self, name):
        """
        Load or create a secret key for name.
        """
        filename = os.path.join(self.key_path, "%s.key" % name)
        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            key = binascii.hexlify(os.urandom(32)).decode("utf-8")
            with open(filename, "w+") as f:
                f.write(key)
        else:
            with open(filename) as f:
                key = f.read()
        return key

    def after_request(self, function):
        """
        Decorator
        """
        return function

    def login_required(self, function):
        """
        Decorator
        """
        ## decorate function here
        return function

    def template_filter(self):
        """
        Decorator
        """
        def decorator(function):
            return function
        return decorator

    def get_template_folder(self):
        return self._template_folder

    def set_template_folder(self, value):
        self._template_folder = os.path.abspath(value)

    def get_static_folder(self):
        return self._static_folder

    def set_static_folder(self, value):
        self._static_folder = value

    def get_sass_folder(self):
        return self._sass_folder

    def set_sass_folder(self, value):
        self._sass_folder = value

## Singleton for the Application
## Allows it to be in scope for decorating the app's
## methods and functions
app = Application()
