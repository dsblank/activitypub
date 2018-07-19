import uuid

class Manager():
    """
    Manager class that ties together ActivityPub objects, defaults,
    and a database.

    >>> from activitypub import Manager
    >>> from activitypub.database import DummyDatabase
    >>> db = DummyDatabase()
    >>> manager = Manager(database=db)
    >>>
    """
    def __init__(self, context=None, defaults=None, database=None):
        from .classes import ActivityPubBase
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

    def from_dict(self, data):
        from .classes import ActivityPubBase
        return ActivityPubBase.from_dict(data)

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

