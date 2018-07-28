import mimetypes
import copy

class ActivityPubBase():
    CLASSES = {}

    def __init__(self, manager=None, **kwargs):
        self.manager = manager
        self.ap_type = self.__class__.__name__
        # First, populate with kwargs:
        for keyword in kwargs:
            if keyword in []:
                setattr(self, keyword, kwargs[keyword])
            else:
                setattr(self, "ap_" + keyword, kwargs[keyword])
        if self.manager and self.manager.defaults:
            # Next, fill in field-defaults:
            for key in self.manager.defaults:
                # Person.id
                if key.startswith(self.ap_type + "."):
                    attr = copy.deepcopy(self.manager.defaults[key])
                    if callable(attr):
                        attr = attr()
                    attr_name = "ap_" + key[len(self.ap_type + "."):]
                    if getattr(self, attr_name) is None:
                        setattr(self, attr_name, attr)
                    elif isinstance(attr, str) and "$" + attr_name[3:] in attr:
                        ## recursive:
                        setattr(self, attr_name,
                                attr.replace("$" + attr_name[3:], getattr(self, attr_name)))
            ## Now expand the field defaults, and build dependencies:
            dependencies = {}
            for attr_name in dir(self):
                if attr_name.startswith("ap_"):
                    attr = getattr(self, attr_name)
                    if isinstance(attr, str) and "$" in attr:
                        parsed = self.manager.parse(attr)
                        dependencies[attr_name[3:]] = {x[1:].split(".")[0] for x in parsed
                                                       if x.startswith("$") and x[1:] != attr_name[3:]}
                    elif isinstance(attr, dict):
                        deps = self.build_dependencies_from_dict(attr, set())
                        for item in deps:
                            dependencies[attr_name[3:]] = dependencies.get(key, set())
                            dependencies[attr_name[3:]].add(item)
            ## Now, replace them in order:
            for attr_name in self.topological_sort(dependencies):
                if "$" + attr_name in self.manager.defaults:
                    attr = copy.deepcopy(self.manager.defaults["$" + attr_name])
                else:
                    if hasattr(self, "ap_" + attr_name):
                        attr = getattr(self, "ap_" + attr_name)
                    elif "." in attr_name:
                        attr = self.get_item_from_dotted(attr_name)
                    else:
                        raise Exception("unknown variable: %s" % attr_name)
                if callable(attr):
                    attr = attr()
                if attr is None:
                    raise Exception("variable depends on field that is empty: %s" % attr_name)
                if isinstance(attr, str) and "$" in attr:
                    setattr(self, attr_name, self.manager.expand_defaults(attr, self))
                elif isinstance(attr, dict):
                    ## traverse dict recursively, looking for replacements:
                    self.replace_items_in_dict(attr)
            ## Finally, remove any temporary variables:
            for attr_name in dir(self):
                if attr_name.startswith("ap_temp"):
                    del self.__dict__[attr_name]

    def get_item_from_dotted(self, dotted_word):
        """
        Get dictionary item from a dotted-word.

        >>> n = Note()
        >>> n.key1 = {"key2": {"key3": 42}}
        >>> n.get_item_from_dotted("key1.key2.key3")
        42
        >>> n.ap_key4 = {"key5": {"key6": 43}}
        >>> n.get_item_from_dotted("key4.key5.key6")
        43
        """
        current = {key: getattr(self, key) for key in dir(self)}
        for word in dotted_word.split("."):
            if "ap_" + word in current:
                current = current["ap_" + word]
            elif word in current:
                current = current[word]
            else:
                return None
        return current

    def build_dependencies_from_dict(self, dictionary, s):
        """
        Given {"val": "$x"} return set("x")
        s is a set, returns s with dependencies.

        >>> n = Note()
        >>> n.build_dependencies_from_dict({"val": "$x"}, set())
        {'x'}
        >>> n.build_dependencies_from_dict({"key1": {"val": "$x"}}, set())
        {'x'}
        >>> s = n.build_dependencies_from_dict({"key1": {"val": "$x"},
        ...                                     "key2": {"key3": "$y"}}, set())
        >>> "x" in s
        True
        >>> "y" in s
        True
        >>> len(s)
        2
        """
        for key in dictionary:
            if isinstance(dictionary[key], str):
                if dictionary[key].startswith("$"):
                    s.add(dictionary[key][1:])
            elif isinstance(dictionary[key], dict):
                self.build_dependencies_from_dict(dictionary[key], s)
        return s

    def replace_items_in_dict(self, dictionary):
        """
        Replace the "$x" in {"val": "$x"} with self.ap_x

        >>> n = Note()
        >>> n.ap_x = 41
        >>> n.ap_y = 43
        >>> dictionary = {"key1": {"val": "$x"},
        ...               "key2": {"key3": "$y"}}
        >>> n.replace_items_in_dict(dictionary)
        >>> dictionary
        {'key1': {'val': 41}, 'key2': {'key3': 43}}
        """
        for key in dictionary:
            if isinstance(dictionary[key], str):
                if dictionary[key].startswith("$"):
                    dictionary[key] = getattr(self, "ap_" + dictionary[key][1:])
            elif isinstance(dictionary[key], dict):
                self.replace_items_in_dict(dictionary[key])

    def topological_sort(self, data):
        """

        >>> from activitypub.manager import Manager
        >>> manager = Manager()
        >>> manager.Person(id="alyssa").to_dict()
        {'@context': 'https://www.w3.org/ns/activitystreams', 'endpoints': {}, 'followers': 'https://example.com/alyssa/followers', 'following': 'https://example.com/alyssa/following', 'id': 'https://example.com/alyssa', 'inbox': 'https://example.com/alyssa/inbox', 'liked': 'https://example.com/alyssa/liked', 'likes': 'https://example.com/alyssa/likes', 'outbox': 'https://example.com/alyssa/outbox', 'type': 'Person', 'url': 'https://example.com/alyssa'}
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

    def to_dict(self):
        """
        Convert object to JSON format.
        """
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
    def from_dict(cls, data):
        if data["type"] in ActivityPubBase.CLASSES.keys():
            obj = ActivityPubBase.CLASSES[data["type"]]()
        else:
            obj = Object()
        for key in data:
            if key not in ["@context"]:
                setattr(obj, "ap_" + key, data[key])
        return obj

    def __getattr__(self, attr):
        if "ap_" + attr in dir(self):
            return getattr(self, "ap_" + attr)
        else:
            raise AttributeError("no such attribute: %s" % attr)

    def __setattr__(self, attr, value):
        if attr == "icon":
            if value:
                self.ap_icon = self.make_icon(value)
            else:
                self.ap_icon = None
        else:
            if "ap_" + attr in dir(self):
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

    def make_icon(self, url):
        return {
            "mediaType": mimetypes.guess_type(url)[0],
            "type": "Image",
            "url": url,
        }

class Actor(Object):
    ap_type = None

    ap_inbox = None
    ap_outbox = None

    ap_following = None
    ap_followers = None
    ap_liked = None
    ap_streams = None
    ap_preferredUsername = None
    ap_endpoints = {}
    ap_sharedInbox = None

class Application(Actor):
    ap_type = "Application"

class Group(Actor):
    ap_type = "Group"

class Organization(Actor):
    ap_type = "Organization"

class Person(Actor):
    """
    >>> from activitypub.manager import Manager
    >>> m = Manager()
    >>> p = m.Person()
    >>> p.icon = "image.svg"
    >>> p.icon
    {'mediaType': 'image/svg+xml', 'type': 'Image', 'url': 'image.svg'}
    """
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

class Activity(Document):
    """
    """
    ap_type = "Activity"

class Create(Object):
    """
    """
    ap_type = "Create"

ActivityPubBase.CLASSES = {
    "Actor": Actor,
    "Activity": Activity,
    "Application": Application,
    "Group": Group,
    "Create": Create,
    "Organization": Organization,
    "Person": Person,
    "Service": Service,
    "Profile": Profile,
    "Document": Document,
    "Note": Note,
    "Relationship": Relationship,
    "Link": Link,
}
