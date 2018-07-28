import mimetypes

class ActivityPubBase():
    CLASSES = {}

    def __init__(self, manager=None, **kwargs):
        self.manager = manager
        self.ap_type = self.__class__.__name__
        ## Handle keywords:
        do_not_expand = False
        if "do_not_expand" in kwargs:
            do_not_expand = kwargs["do_not_expand"]
            del kwargs["do_not_expand"]
        # First, populate with kwargs:
        for keyword in kwargs:
            if keyword in []:
                setattr(self, keyword, kwargs[keyword])
            else:
                setattr(self, "ap_" + keyword, kwargs[keyword])
        if do_not_expand:
            return
        if self.manager and self.manager.defaults:
            self.manager.fill_in_defaults(self)
            ## Now expand the field defaults, and build dependencies:
            self.manager.fill_in_deep_defaults(self)
            ## Finally, remove any temporary variables:
            for attr_name in dir(self):
                if attr_name.startswith("ap_temp"):
                    ## move to just "temp_"
                    self.__dict__[attr_name[3:]] =  getattr(self, attr_name)
                    del self.__dict__[attr_name]

    def to_dict(self):
        """
        Convert object to JSON format.
        """
        retval = {}
        if self.ap_context is not None:
            retval["@context"] = self.ap_context
        elif self.manager and self.manager.context:
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
            if key == "@context":
                setattr(obj, "ap_context", data[key])
            else:
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
