### This file and folder are based on:
### https://github.com/tsileo/microblog.pub
### https://github.com/tsileo/little-boxes

### Work In Progress! When complete, this
### file should only contain the specific
### logic for a micro blog.

from html2text import html2text
from urllib.parse import urlparse
import bleach
import logging

logging.getLogger().setLevel(logging.DEBUG)

from activitypub import VERSION
from activitypub.manager.base import app
from activitypub.bson import ObjectId

## Pick one:
from activitypub.manager import FlaskManager as Manager
#from activitypub.manager import TornadoManager as Manager
#from activitypub.manager import Manager as Manager

from activitypub.database import *
## Pick one:
database = RedisDatabase("redis://localhost:6379/0")
#database = MongoDatabase("mongodb://localhost:27017", "dsblank_localhost:5000")
#database = ListDatabase(),
#database = SQLDatabase("sqlite://"),
#datavbase = SQLDatabase("sqlite:///sqlite.db"),

"""
### Some fake data:

database.activities.clear()
database.actors.clear()

for id in ["dsblank", "alyssa", "jones", "smith"]:
    person = manager.Person(**{"id": id,
                               "temp_id": id,
                               'name': "$temp_id",
                               'preferredUsername': "$temp_id",
    })
    if not database.actors.find_one({"id": person.id}):
        database.actors.insert_one(person.to_dict())

for i in range(10):
    person = manager.Person(id="dsblank")
    text = "This is note #%s" % i
    note = manager.Note(
        **{
            'sensitive': False,
            'attributedTo': '$DOMAIN',
            'cc': ['$DOMAIN/followers'],
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'content': '<p>$source.content</p>',
            'tag': [],
            'source': {'mediaType': 'text/markdown', 'content': text},
            'published': '$NOW',
            'temp_uuid': "$UUID",
            'id': '$DOMAIN/outbox/$temp_uuid/activity',
            'url': '$DOMAIN/note/$temp_uuid',
        })
    create = manager.Create(
        **{
            'context': ['https://www.w3.org/ns/activitystreams',
                         'https://w3id.org/security/v1',
                         {'Hashtag': 'as:Hashtag',
                          'sensitive': 'as:sensitive',
                          'toot': 'http://joinmastodon.org/ns#',
                          'featured': 'toot:featured'}],
            'actor': '$DOMAIN',
            'object': note.to_dict(),
            'published': '$NOW',
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': ['$DOMAIN/followers'],
            'id': '$DOMAIN/outbox/%s' % note.temp_uuid,
        }
    )
    message = manager.Create(
        **{
            'activity': create.to_dict(),
            'box': 'outbox',
            'type': ['Create'],
            'remote_id': '$DOMAIN/outbox/%s' % note.temp_uuid,
            'meta': {'undo': False, 'deleted': False},
            })
    
    database.activities.insert_one(message.to_dict())
"""

manager = Manager(database=database)
manager.setup_css()
## FIXME: get rid of all of these:
manager.config.update({
    "ME": {
        "url": "https://example.com",
        "icon": {"url": "https://example.com"},
        "icon_url": 'https://cs.brynmawr.edu/~dblank/images/doug-sm-orig.jpg',
        "summary": "I'm just me."},
    "NAME": "ActivityPub Blog",
    "ID": "http://localhost:%s/dsblank" % manager.port,
    "BASE_URL": "http://localhost:%s" % manager.port, 
    })

#### The routes:

@app.route("/notes", endpoint="notes")
@app.route("/")
def route_index(self, *args, **kwargs):
    logging.info("args: %s,  kwargs: %s" % (args, kwargs))
    q = {
        "box": "outbox",
        "type": {"$in": ["Create", "Announce"]},
        "activity.object.inReplyTo": None,
        "meta.deleted": False,
        "meta.undo": False,
    }
    outbox_data, older_than, newer_than = paginated_query(self, self.database.activities, q)
    logging.info("outbox_data: %s" % outbox_data)
    return self.render_template(
        "index.html",
        outbox_data=outbox_data,
        older_than=older_than,
        newer_than=newer_than,
    )

@app.route("/admin", methods=["GET"])
#@login_required
def route_admin(self):
    q = {
        "meta.deleted": False,
        "meta.undo": False,
        "type": "like",
        "box": "outbox",
    }
    col_liked = self.database.activities.count(q)

    return self.render_template(
        "admin.html",
        instances=list(self.database.instances.find()),
        inbox_size=self.database.activities.count({"box": "inbox"}),
        outbox_size=self.database.activities.count({"box": "outbox"}),
        col_liked=col_liked,
        col_followers=self.database.activities.count(
            {
                "box": "inbox",
                "type": "follow",
                "meta.undo": False,
            }
        ),
        col_following=self.database.activities.count(
            {
                "box": "outbox",
                "type": "follow",
                "meta.undo": False,
            }
        ),
    )

@app.route("/login", methods=["POST", "GET"])
def route_login(self):
    return self.redirect(
        self.get_argument("redirect", None) or self.url_for("admin_notifications")
    )

@app.route("/admin/notifications")
def admin_notifications(self):
    # FIXME(tsileo): show unfollow (performed by the current actor) and liked???
    mentions_query = {
        "type": "Create",
        "activity.object.tag.type": "Mention",
        "activity.object.tag.name": "@dsblank@https://example.com",
        "meta.deleted": False,
    }
    replies_query = {
        "type": "Create",
        "activity.object.inReplyTo": {"$regex": "^https://example.com"},
    }
    announced_query = {
        "type": "Announce",
        "activity.object": {"$regex": "^https://example.com"},
    }
    new_followers_query = {"type": "Follow"}
    unfollow_query = {
        "type": "Undo",
        "activity.object.type": "Follow",
    }
    followed_query = {"type": "Accept"}
    q = {
        "box": "inbox",
        "$or": [
            mentions_query,
            announced_query,
            replies_query,
            new_followers_query,
            followed_query,
            unfollow_query,
        ],
    }
    inbox_data, older_than, newer_than = paginated_query(self, self.database.activities, q)

    return self.render_template(
        "stream.html",
        inbox_data=inbox_data,
        older_than=older_than,
        newer_than=newer_than,
    )

### FIXME: move paging to Manager
def paginated_query(self, db, q, limit=5, sort_key="_id"):
    older_than = newer_than = None
    query_sort = -1
    first_page = (not self.get_argument("older_than", None) and
                  not self.get_argument("newer_than", None))

    query_older_than = self.get_argument("older_than", None)
    query_newer_than = self.get_argument("newer_than", None)

    if query_older_than:
        q["_id"] = {"$lt": ObjectId(query_older_than)}
    elif query_newer_than:
        q["_id"] = {"$gt": ObjectId(query_newer_than)}
        query_sort = 1

    outbox_data = list(db.find(q, limit=limit + 1).sort(sort_key, query_sort))
    outbox_len = len(outbox_data)
    outbox_data = sorted(
        outbox_data[:limit], key=lambda x: str(x[sort_key]), reverse=True
    )
    if query_older_than:
        newer_than = str(outbox_data[0]["_id"])
        if outbox_len == limit + 1:
            older_than = str(outbox_data[-1]["_id"])
    elif query_newer_than:
        older_than = str(outbox_data[-1]["_id"])
        if outbox_len == limit + 1:
            newer_than = str(outbox_data[0]["_id"])
    elif first_page and outbox_len == limit + 1:
        older_than = str(outbox_data[-1]["_id"])
    return outbox_data, older_than, newer_than

    
@app.context_processor
def context_processor(self):
    q = {
        "type": "Create",
        "activity.object.type": "Note",
        "activity.object.inReplyTo": None,
        "meta.deleted": False,
    }
    notes_count = self.database.activities.find(
        {"box": "outbox", "$or": [q, {"type": "Announce", "meta.undo": False}]}
    ).count()
    q = {"type": "Create", "activity.object.type": "Note", "meta.deleted": False}
    with_replies_count = self.database.activities.find(
        {"box": "outbox", "$or": [q, {"type": "Announce", "meta.undo": False}]}
    ).count()
    liked_count = self.database.activities.count(
        {
            "box": "outbox",
            "meta.deleted": False,
            "meta.undo": False,
            "type": "Like",
        }
    )
    followers_q = {
        "box": "inbox",
        "type": "follow",
        "meta.undo": False,
    }
    following_q = {
        "box": "outbox",
        "type": "follow",
        "meta.undo": False,
    }
    return {
        "microblogpub_version": VERSION,
        "followers_count": self.database.activities.count(followers_q),
        "following_count": self.database.activities.count(following_q),
        "notes_count": notes_count,
        "liked_count": liked_count,
        "with_replies_count": with_replies_count,
        "DOMAIN": "localhost:%s/test" % (self.port,), # TODO: update on each fetch, include full URL, /test
    }

@app.route("/test")
def route_test(self):
    return self.render_template("test.html")

### The filters:

@app.filter
def html2plaintext(self, body, *args, **kwargs):
    return html2text(body)

def _to_list(item):
    if not isinstance(item, list):
        return list(item)
    return item

@app.filter
def has_type(self, doc, _type):
    if _type in _to_list(doc["type"]):
        return True
    return False

@app.filter
def get_actor(self, url):
    retval = self.database.actors.find_one({"id": self.config["ID"]})
    if retval is not None:
        return retval

@app.filter
def get_url(self, u):
    if isinstance(u, dict):
        return u["href"]
    elif isinstance(u, str):
        return u
    else:
        return u

@app.filter
def get_actor_icon_url(self, url, size):
    return _get_file_url(url, size, Kind.ACTOR_ICON)

@app.filter
def domain(self, url):
    return urlparse(url).netloc

@app.filter
def permalink_id(self, val):
    return str(hash(val))

@app.filter
def is_from_outbox(self, t):
    logging.warning("is_from_outbox(%s)" % (t,))
    return True
    return t.startswith(ID)

@app.filter
def format_timeago(self, val):
    return "OK"
    if val:
        dt = parser.parse(val)
        return timeago.format(dt, datetime.now(timezone.utc))
    return val

# HTML/templates helper
ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "br",
    "blockquote",
    "code",
    "pre",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
    "span",
    "div",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]

def clean_html(html):
    return bleach.clean(html, tags=ALLOWED_TAGS)

@app.filter
def clean(self, html):
    return clean_html(html)

@app.filter
def not_only_imgs(self, attachment):
    for a in attachment:
        if not _is_img(a["url"]):
            return True
    return False

@app.filter
def is_img(self, filename):
    return _is_img(filename)

@app.filter
def get_attachment_url(self, url, size):
    return _get_file_url(url, size, Kind.ATTACHMENT)

@app.filter
def format_time(self, val):
    return "OK"
    if val:
        dt = parser.parse(val)
        return datetime.strftime(dt, "%B %d, %Y, %H:%M %p")
    return val

@app.filter
def quote_plus(self, t):
    import urllib
    return urllib.parse.quote_plus(t)

if __name__ == "__main__":
    manager.run()
