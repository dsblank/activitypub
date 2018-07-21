import binascii
import os
import uuid

class Manager():
    """
    Manager class that ties together ActivityPub objects, defaults,
    and a database.

    >>> from activitypub.manager import Manager
    >>> from activitypub.database import DummyDatabase
    >>> db = DummyDatabase()
    >>> manager = Manager(database=db)
    >>>
    """
    app_name = "activitypub"
    version = "1.0.0"
    def __init__(self, context=None, defaults=None, database=None):
        from ..classes import ActivityPubBase
        self.callback = lambda box, activity_id: None
        self.context = context
        self.defaults = defaults or self.make_defaults()
        self.defaults["$UUID"] = lambda: str(uuid.uuid4())
        self.database = database

        def make_wrapper(manager, class_):
            def wrapper(*args, **kwargs):
                return ActivityPubBase.CLASSES[class_](manager, *args, **kwargs)
            return wrapper

        for class_ in ActivityPubBase.CLASSES:
            setattr(self, class_, make_wrapper(self, class_))

    def make_defaults(self):
        """
        A default field can refer to itself, which means that it needs a
        value to begin with.

        >>> m = Manager()
        >>> n = m.Note(attributedTo="alyssa", id="23")
        >>> n.to_dict()
        {'@context': 'https://www.w3.org/ns/activitystreams', 'attributedTo': 'alyssa', 'id': 'alyssa/note/23', 'type': 'Note'}

        A default can be a $-variable, or the name of a "Class.field_name".
        """
        return {
            "$SCHEME": "https",
            "$HOST": "example.com",
            "Person.id": "$SCHEME://$HOST/$id",
            "Person.likes": "$id/likes",
            "Person.following": "$id/following",
            "Person.followers": "$id/followers",
            "Person.liked": "$id/liked",
            "Person.inbox": "$id/inbox",
            "Person.outbox": "$id/outbox",
            "Person.url": "$id",
            "Note.id": "$attributedTo/note/$id",
        }

    def user_agent(self):
        return "%s (%s/%s; +%s)" % (requests.utils.default_user_agent(),
                                    self.app_name,
                                    self.version,
                                    self.expand_defaults("$SCHEME/$HOST"))

    def expand_defaults(self, string, obj=None):
        """
        Expand a string with defaults.
        """
        for key in self.defaults:
            if key.startswith("$"):
                if callable(self.defaults[key]):
                    string = string.replace(key, self.defaults[key]())
                else:
                    string = string.replace(key, self.defaults[key])
        if obj:
            for key in self.parse(string):
                if key.startswith("$"):
                    if getattr(obj, "ap_" + key[1:]) is None:
                        raise Exception("expansion requires %s" % key[1:])
                    string = string.replace(key, getattr(obj, "ap_" + key[1:]))
        return string

    def parse(self, string):
        """
        Parse a string delimited by non-alpha, non-$ symbols.

        >>> from activitypub.manager import Manager
        >>> m = Manager()
        >>> m.parse("apple/banana/$variable")
        ['apple', 'banana', '$variable']
        """
        retval = []
        current = []
        for s in string:
            if s.isalpha() or (s in ["$"] and len(current) == 0):
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

    def get_secret_key(self, name):
        filename = "%s.key" % name
        if not os.path.exists():
            key = binascii.hexlify(os.urandom(32)).decode("utf-8")
            with open(filename, "w+") as f:
                f.write(key)
            return key
        else:
            with open(key_path) as f:
                return f.read()

    def get_rsa_key(self, owner, user, domain):
        """"
        Loads or generates an RSA key.
        """
        k = Key(owner)
        user = user.replace(".", "_")
        domain = domain.replace(".", "_")
        key_path = os.path.join(KEY_DIR, f"key_{user}_{domain}.pem")
        if os.path.isfile(key_path):
            with open(key_path) as f:
                privkey_pem = f.read()
                k.load(privkey_pem)
        else:
            k.new()
            with open(key_path, "w") as f:
                f.write(k.privkey_pem)
        return k

    def after_request(self, f):
        """
        Decorator
        """
        return f

    def template_filter(self):
        """
        Decorator
        """
        def decorator(f):
            return f
        return decorator