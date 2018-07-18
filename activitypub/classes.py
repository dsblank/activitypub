import uuid

class Manager():
    """

    >>> from activitypub import ListDatabase, Manager
    >>> db = ListDatabase()
    >>> manager = Manager(database=db)
    >>>
    """
    def __init__(self, context=None, defaults=None, database=None):
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
        return {
            "$SCHEME": "https",
            "$HOST": "example.com",
            "Person.likes": "$id/likes",
            "Note.id": "$attributedTo/$UUID",
        }

    def from_json(self, data):
        return ActivityPubBase.from_json(data)

    def to_list(self, item):
        if isinstance(item, list):
            return item
        return [item]

    def on_post_to_box(self, box, activity):
        """
        manager.on_post_to_box("inbox", activity)
        """
        self.database.activities.insert_one(
            {
                "box": box,
                "activity": activity.to_json(),
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

class ActivityPubBase():
    CLASSES = {}

    def __init__(self, manager=None, **kwargs):
        self.manager = manager
        self.ap_type = self.__class__.__name__
        for keyword in kwargs:
            if keyword in []:
                setattr(self, keyword, kwargs[keyword])
            else:
                setattr(self, "ap_" + keyword, kwargs[keyword])
        if self.manager and self.manager.defaults:
            ## First, replace all fields with field defaults if value is None:
            for key in self.manager.defaults:
                if key.startswith(self.ap_type + "."):
                    attr = self.manager.defaults[key]
                    attr_name = "ap_" + key[len(self.ap_type + "."):]
                    if getattr(self, attr_name) is None:
                        setattr(self, attr_name, attr)
                    elif "$" + attr_name[3:] in attr:
                        ## recursive:
                        setattr(self, attr_name,
                                attr.replace("$" + attr_name[3:], getattr(self, attr_name)))
            ## Now expand the field defaults:
            for attr_name in dir(self):
                if attr_name.startswith("ap_"):
                    attr = getattr(self, attr_name)
                    if attr is not None and "$" in attr:
                        setattr(self, attr_name, self.expand_defaults(attr))

    def expand_defaults(self, string):
        def parse(string):
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
        for key in self.manager.defaults:
            if key.startswith("$"):
                if callable(self.manager.defaults[key]):
                    string = string.replace(key, self.manager.defaults[key]())
                else:
                    string = string.replace(key, self.manager.defaults[key])
        for key in parse(string):
            if key.startswith("$"):
                if getattr(self, "ap_" + key[1:]) is None:
                    raise Exception("expansion requires %s" % key[1:])
                string = string.replace(key, getattr(self, "ap_" + key[1:]))
        return string

    def to_json(self):
        retval = {}
        if self.manager and self.manager.context:
            retval["@context"] = self.manager.context
        else:
            retval["@context"] = "https://www.w3.org/ns/activitystreams"
        for attr_name in dir(self):
            if attr_name.startswith("ap_"):
                attr = getattr(self, attr_name)
                if attr is not None:
                    retval[attr_name[3:]] = attr
        return retval

    @classmethod
    def from_json(cls, data):
        if data["type"] in ActivityPubBase.CLASSES.keys():
            obj = ActivityPubBase.CLASSES[data["type"]]()
        else:
            obj = Object()
        for key in data:
            if key not in ["@context"]:
                setattr(obj, "ap_" + key, data[key])
        return obj

    def __getattr__(self, attr):
        if "ap_" + attr in self.__dict__:
            return getattr(self, "ap_" + attr)
        else:
            raise AttributeError("no such attribute: %s" % attr)

    def __setattr__(self, attr, value):
        if "ap_" + attr in self.__dict__:
            setattr(self, "ap_" + attr, value)
        else:
            self.__dict__[attr] = value

class Object(ActivityPubBase):
    ap_id = None
    ap_attachment = None
    ap_attributedTo = None
    ap_audience = None
    ap_content = None
    ap_context = None
    ap_name = None
    ap_endTime = None
    ap_generator = None
    ap_icon = None
    ap_image = None
    ap_inReplyTo = None
    ap_location = None
    ap_preview = None
    ap_published = None
    ap_replies = None
    ap_startTime = None
    ap_summary = None
    ap_tag = None
    ap_updated = None
    ap_url = None
    ap_to = None
    ap_bto = None
    ap_cc = None
    ap_bcc = None
    ap_mediaType = None
    ap_duration = None
    ap_likes = None

class Actor(Object):
    ap_type = None

    ap_inbox = None
    ap_outbox = None

    ap_followers = None
    ap_liked = None
    ap_streams = None
    ap_preferredUsername = None
    ap_endpoints = None
    ap_sharedInbox = None

    def on_post(self, activity):
        if activity.type != "Create":
            obj = activity.object
        else:
            obj = activity

class Application(Actor):
    ap_type = "Application"

class Group(Actor):
    ap_type = "Group"

class Organization(Actor):
    ap_type = "Organization"

class Person(Actor):
    ap_type = "Person"

class Service(Actor):
    ap_type = "Service"

class Profile(Object):
    ap_type = "Profile"
    ap_describes = None

class Document(Object):
    ap_type = "Document"

class Relationship(Object):
    ap_subject = None
    ap_object = None
    ap_relationship = None

class Link(ActivityPubBase):
    ap_type = "Link"
    ap_href = None
    ap_rel = None
    ap_mediaType = None
    ap_name = None
    ap_hreflang = None
    ap_height = None
    ap_width = None
    ap_preview = None

class Note(Document):
    """
    """
    ap_type = "Note"

class Create(Object):
    """
    """
    ap_type = "Create"

ActivityPubBase.CLASSES = {
    "Actor": Actor,
    "Application": Application,
    "Group": Group,
    "Organization": Organization,
    "Person": Person,
    "Service": Service,
    "Profile": Profile,
    "Document": Document,
    "Note": Note,
    "Relationship": Relationship,
    "Link": Link,
}
