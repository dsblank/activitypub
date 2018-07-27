import re

from .base import app

WEBFINGER = re.compile(r'(?:acct:)?(?P<username>[\w.!#$%&\'*+-/=?^_`{|}~]+)@(?P<host>[\w.:-]+)')

@app.route("/user/<nickname>", ["GET"])
def route_user(self, nickname):
    #obj = self.database.actors.find_one(id=nickname)
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/publickey", ["GET"])
def route_publickey(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/outbox", ["GET"])
def route_user_outbox(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/outbox/<page>", ["GET"])
def route_outbox_page(self, nickname, page):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

#@app.route("/user/<nickname>/outbox", ["POST"])
#def route_(self):
#    return self.render_template("test.html")

@app.route("/user/<nickname>/inbox", ["GET"])
def route_inbox(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/inbox/<page>", ["GET"])
def route_inbox_page(self, nickname, page):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

#@app.route("/user/<nickname>/inbox", ["POST"])
#def route_(self):
#    return self.render_template("test.html")

@app.route("/user/<nickname>/followers", ["GET"])
def route_followers(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/followers/<page>", ["GET"])
def route_followers_page(self, nickname, page):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/following", ["GET"])
def route_following(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/following/<page>", ["GET"])
def route_following_page(self, nickname, page):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/liked", ["GET"])
def route_liked(self, nickname):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/user/<nickname>/liked/<page>", ["GET"])
def route_liked_page(self, nickname, page):
    obj = self.Actor(id=nickname)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>", ["GET"])
def route_activity(self, uuid):
    obj = self.manager.Note(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/replies", ["GET"])
def route_activity_replies(self, uuid):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/replies/<page>", ["GET"])
def route_activity_replies_page(self, uuid, page):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/likes", ["GET"])
def route_activity_likes(self, uuid):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/likes/<page>", ["GET"])
def route_activity_likes_page(self, uuid, page):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/shares", ["GET"])
def route_activity_shares(self, uuid):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/activity/<uuid>/shares/<page>", ["GET"])
def route_activity_shares_page(self, uuid, page):
    obj = self.Activity(id=uuid)
    if obj:
        return self.render_json(
            obj.to_dict()
        )
    else:
        return self.error(404)

@app.route("/content/<uuid>", ["GET"])
def route_content(self, uuid):
    return self.render_template(
        "test.html",
        uuid=uuid,
    )

@app.route("/content/<uuid>/replies", ["GET"])
def route_content_replies(self, uuid):
    return self.render_template(
        "test.html",
        uuid=uuid,
    )

@app.route("/content/<uuid>/replies/<page>", ["GET"])
def route_content_replies_page(self, uuid, page):
    return self.render_template(
        "test.html",
        uuid=uuid,
        page=page,
    )

@app.route("/content/<uuid>/likes", ["GET"])
def route_content_likes(self, uuid):
    return self.render_template(
        "test.html",
        uuid=uuid,
    )

@app.route("/content/<uuid>/likes/<page>", ["GET"])
def route_content_likes_page(self, uuid, page):
    return self.render_template(
        "test.html",
        uuid=uuid,
        page=page,
    )

@app.route("/content/<uuid>/shares", ["GET"])
def route_content_shares(self, uuid):
    return self.render_template(
        "test.html",
        uuid=uuid,
    )

@app.route("/content/<uuid>/shares/<page>", ["GET"])
def route_content_shares_page(self, uuid, page):
    return self.render_template(
        "test.html",
        uuid=uuid,
        page=page,
    )

@app.route("/.well-known/webfinger", ["GET"])
def route_webfinger(self):
    """
    ?resource=acct:bob@my-example.com
    """
    resource = self.get_argument("resource")
    obj = None
    if resource:
        matches = WEBFINGER.match(resource)
        if matches:
            username = matches["username"]
            host = matches["host"]
            id = "https://%s/%s" % (host, username)
            obj = self.database.actors.find_one({"id":id})
    ## Add a temp person:
    #obj = self.Person(id="dsblank")
    #self.database.actors.insert_one(obj.to_dict())
    if obj:
        return self.render_json({
            "subject": resource,
            "links": [{
                "rel": "self",
                "type": "application/activity+json",
                "href": obj["id"]
            }]
        })
    else:
        return self.error(404)

"""

{
  "subject": "acct:will@willnorris.com",
  "aliases": [
    "mailto:will@willnorris.com",
    "https://willnorris.com/"
  ],
  "links": [
    {
      "rel": "http://webfinger.net/rel/avatar",
      "href": "https://willnorris.com/logo.jpg",
      "type": "image/jpeg"
    },
    {
      "rel": "http://webfinger.net/rel/profile-page",
      "href": "https://willnorris.com/",
      "type": "text/html"
    }
  ]
}

{
 "subject": "acct:alice@my-example.com",
 "links": [
    {
      "rel": "self",
      "type": "application/activity+json",
      "href": "https://my-example.com/actor"
    }
 ]
}
"""

# /api/v1/instance

"""
{
    "uri":"mastodon.social",
    "title":"Mastodon",
    "description":"This page describes the mastodon.social \u003cem\u003einstance\u003c/em\u003e - wondering what Mastodon is? Check out \u003ca href=\"https://joinmastodon.org\"\u003ejoinmastodon.org\u003c/a\u003e instead! In essence, Mastodon is a decentralized, open source social network. This is just one part of the network, run by the main developers of the project \u003cimg draggable=\"false\" alt=\"🐘\" class=\"emojione\" src=\"https://mastodon.social/emoji/1f418.svg\" /\u003e It is not focused on any particular niche interest - everyone is welcome as long as you follow our code of conduct!",
    "email":"hello@joinmastodon.org",
    "version":"2.4.3",
    "urls": {
        "streaming_api":"wss://mastodon.social"
    },
    "stats": {
        "user_count":171746,
        "status_count":6467133,
        "domain_count":5177
    },
    "thumbnail":"https://files.mastodon.social/site_uploads/files/000/000/001/original/DN5wMUeVQAENPwp.jpg_large.jpeg",
    "languages":["en"],
    "contact_account": {
        "id":"1",
        "username":"Gargron",
        "acct":"Gargron",
        "display_name":"Eugen",
        "locked":false,
        "bot":false,
        "created_at":"2016-03-16T14:34:26.392Z",
        "note":"\u003cp\u003eDeveloper of Mastodon. 25\u003c/p\u003e",
        "url":"https://mastodon.social/@Gargron",
        "avatar":"https://files.mastodon.social/accounts/avatars/000/000/001/original/eb9e00274b135808.png",
        "avatar_static":"https://files.mastodon.social/accounts/avatars/000/000/001/original/eb9e00274b135808.png",
        "header":"https://files.mastodon.social/accounts/headers/000/000/001/original/af58e4df0e8b3e15.png",
        "header_static":"https://files.mastodon.social/accounts/headers/000/000/001/original/af58e4df0e8b3e15.png",
        "followers_count":92732,
        "following_count":530,
        "statuses_count":40388,
        "emojis":[],
        "fields":[
            {
                "name":"Patreon",
                "value":"\u003ca href=\"https://www.patreon.com/mastodon\" rel=\"me nofollow noopener\" target=\"_blank\"\u003e\u003cspan class=\"invisible\"\u003ehttps://www.\u003c/span\u003e\u003cspan class=\"\"\u003epatreon.com/mastodon\u003c/span\u003e\u003cspan class=\"invisible\"\u003e\u003c/span\u003e\u003c/a\u003e"
            },
            {
                "name":"Liberapay",
                "value":"\u003ca href=\"https://liberapay.com/Mastodon/\" rel=\"me nofollow noopener\" target=\"_blank\"\u003e\u003cspan class=\"invisible\"\u003ehttps://\u003c/span\u003e\u003cspan class=\"\"\u003eliberapay.com/Mastodon/\u003c/span\u003e\u003cspan class=\"invisible\"\u003e\u003c/span\u003e\u003c/a\u003e"
            }
        ]
    }
}
"""
