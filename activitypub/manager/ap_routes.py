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
From: https://github.com/tootsuite/mastodon/blob/master/spec/fixtures/requests/activitypub-webfinger.txt

HTTP/1.1 200 OK
Cache-Control: max-age=0, private, must-revalidate
Content-Type: application/jrd+json; charset=utf-8
X-Content-Type-Options: nosniff
Date: Sun, 17 Sep 2017 06:22:50 GMT

{"subject":"acct:foo@ap.example.com","aliases":["https://ap.example.com/@foo","https://ap.example.com/users/foo"],"links":[{"rel":"http://webfinger.net/rel/profile-page","type":"text/html","href":"https://ap.example.com/@foo"},{"rel":"http://schemas.google.com/g/2010#updates-from","type":"application/atom+xml","href":"https://ap.example.com/users/foo.atom"},{"rel":"self","type":"application/activity+json","href":"https://ap.example.com/users/foo"},{"rel":"salmon","href":"https://ap.example.com/api/salmon/1"},{"rel":"magic-public-key","href":"data:application/magic-public-key,RSA.u3L4vnpNLzVH31MeWI394F0wKeJFsLDAsNXGeOu0QF2x-h1zLWZw_agqD2R3JPU9_kaDJGPIV2Sn5zLyUA9S6swCCMOtn7BBR9g9sucgXJmUFB0tACH2QSgHywMAybGfmSb3LsEMNKsGJ9VsvYoh8lDET6X4Pyw-ZJU0_OLo_41q9w-OrGtlsTm_PuPIeXnxa6BLqnDaxC-4IcjG_FiPahNCTINl_1F_TgSSDZ4Taf4U9XFEIFw8wmgploELozzIzKq-t8nhQYkgAkt64euWpva3qL5KD1mTIZQEP-LZvh3s2WHrLi3fhbdRuwQ2c0KkJA2oSTFPDpqqbPGZ3QvuHQ==.AQAB"},{"rel":"http://ostatus.org/schema/1.0/subscribe","template":"https://ap.example.com/authorize_follow?acct={uri}"}]}

From: https://mastodon.social/.well-known/webfinger?resource=acct:dsblank@mastodon.social

{"subject": "acct:dsblank@mastodon.social",
 "aliases": ["https://mastodon.social/@dsblank",
             "https://mastodon.social/users/dsblank"],
 "links": [ {"rel": "http://webfinger.net/rel/profile-page",
             "type": "text/html",
             "href": "https://mastodon.social/@dsblank"},
            {"rel": "http://schemas.google.com/g/2010#updates-from",
             "type":"application/atom+xml",
             "href":"https://mastodon.social/users/dsblank.atom"},
            {"rel":"self",
             "type":"application/activity+json",
             "href":"https://mastodon.social/users/dsblank"},
            {"rel":"salmon",
             "href":"https://mastodon.social/api/salmon/368878"},
            {"rel":"magic-public-key",
             "href":"data:application/magic-public-key,RSA.3L4-ufnddoOSl-YS6pel0q-tz01cjutYsl6sVM3QkJBX9T3Mp9MCarbbh5xEfttxIPCzZZAv1Yv_VRyOsexPi7CfF8z2pOjaZ-HD7KrwovhgiiL8YIwd_6o3qc5eCUibE56DyemUfqxWWNcvJH64D57cF0sMaZpx95DSQ5JKkcIq2M_M1Wm5AQZH5NIKnVyR55eOH7zN09mvZrK_S93b5DYaeBIjNwgtTBRDj4qqNtRtF5SM3_XmdWskA_KArP586W7CI4ZK538WbnT09JNA3d7TJQrwLXwkXJMX1nQARKQfyjbRbg2lXJcdHV_0pJqnJa9p24O0ysOtPN6LqL6v5w==.AQAB"},
            {"rel":"http://ostatus.org/schema/1.0/subscribe",
             "template":"https://mastodon.social/authorize_follow?acct={uri}"}
          ]
}

From: https://a4.io/.well-known/webfinger?resource=acct:t@a4.io

{"subject": "acct:t@a4.io",
 "aliases": ["https://a4.io"],
 "links": [{"rel": "http://webfinger.net/rel/profile-page",
            "type": "text/html", "href": "https://a4.io"},
           {"rel": "self", "type": "application/activity+json", "href": "https://a4.io"},
           {"rel": "http://ostatus.org/schema/1.0/subscribe", "template": "https://a4.io/authorize_follow?profile={uri}"},
           {"rel": "magic-public-key", "href": "data:application/magic-public-key,RSA.zTYvKgiDIanj3XnpoGPdVmwq0A_FPqcoJXqMpNcIOVzWcOGK1WkxLeOnCcXhnxNnKpnXQIjU8MRz2y1tOfVEZHmII_hnOh2hcS3K5Sd_yHWnQkPgfnSBzn46mx3m8Nwi49qOZ0--ARGzVhOaBJhuUX2MvBrHl2A2GRjRtTnzACqFxB-ezZNGG6Ymvzv7CTCPXKUlygNqDy0Hi48SM_2LSmgotz5L0Vng3q33c9XeGR3YAiUlCevCDTyvIAkzN4hlP5zYezp_Bp7CkoY3teIvCaxZS5n92I_Oj2Xyq60v0MeXiqyXioGNPnUB8QtFV20kEhdwJik0_DubiRP_2Iy65w==.AQAB"},
           {"href": "https://sos-ch-dk-2.exo.io/hexaninja/hexaninja-alpha.png", "rel": "http://webfinger.net/rel/avatar", "type": "image/png"}]
}

From https://willnorris.com/.well-known/webfinger?resource=acct:will@willnorris.com:

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
