# activitypub

This module is designed to be a generally useful ActivityPub library in Python. It targets three different levels of use:

* ActivityPub object API
* ActivityPub database API
* Webserver

The first two levels can be used indpendently, or together. They can best be used toegether using a Manager:

```python
>>> from activitypub import Manager
>>> from activitypub.database import DummyDatabase
>>> db = DummyDatabase()
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
```
