# activitypub

This is a Python library to use with
[ActivityPub](https://en.wikipedia.org/wiki/ActivityPub). ActivityPub
is an API for an open, distributed, social network.

## Install

You can install the development version of activitypub with:

```
pip install git+git://github.com/dsblank/activitypub
```

or the last packaged version with:

```
pip install activitypub
```
To use with redis:

```
pip install redis redis_collections
```

OR to use with mongodb:

```
pip install pymongo
```

OR to use with SQLAlchemy:

```
pip install sqlalchemy
```

## Abstractions

This module is designed to be a generally useful ActivityPub library in Python. It targets three different levels of use:

* ActivityPub object API
* ActivityPub database API
* Webserver API

These levels can be used independently, or together. They can best be used together using a Manager:

```python
>>> from activitypub.manager import Manager
>>> from activitypub.database import ListDatabase
>>> db = ListDatabase()
>>> manager = Manager(database=db)
>>> p = manager.Person(id="alyssa")
>>> p.to_dict()
{'@context': 'https://www.w3.org/ns/activitystreams',
 'endpoints': {},
 'followers': 'https://example.com/alyssa/followers',
 'following': 'https://example.com/alyssa/following',
 'id': 'https://example.com/alyssa',
 'inbox': 'https://example.com/alyssa/inbox',
 'liked': 'https://example.com/alyssa/liked',
 'likes': 'https://example.com/alyssa/likes',
 'outbox': 'https://example.com/alyssa/outbox',
 'type': 'Person',
 'url': 'https://example.com/alyssa'}
>>> db.actors.insert_one(p.to_dict())
>>> db.actors.find_one({"id": 'https://example.com/alyssa'})
{'@context': 'https://www.w3.org/ns/activitystreams',
 'endpoints': {},
 'followers': 'https://example.com/alyssa/followers',
 'following': 'https://example.com/alyssa/following',
 'id': 'https://example.com/alyssa',
 'inbox': 'https://example.com/alyssa/inbox',
 'liked': 'https://example.com/alyssa/liked',
 'likes': 'https://example.com/alyssa/likes',
 'outbox': 'https://example.com/alyssa/outbox',
 'type': 'Person',
 'url': 'https://example.com/alyssa',
 '_id': ObjectId('5b579aee1342a3230c18fbf7')}
```

activitypub supports the following databases:

* MongoDB
* SQL dialects --- any that that sqlalchemy supports, including:
  * SQLite (including in-memory)
  * Firebird
  * Microsoft SQL Server
  * MySQL
  * Oracle
  * PostgreSQL
  * Sybase
  * ... and many more!
* An in-memory, JSON-based database for testing
* Redis

The activitypub database API is a subset of the MongoDB.

activitypub is targeting the following web frameworks:

* Flask
* Tornado

Others can be supported. Please ask!

The activitypub webservice API is based on Flask's.

## Applications

* [Blog](https://github.com/dsblank/activitypub/tree/master/apps/blog)
