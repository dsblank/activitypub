import re
import ast
import json
import copy

from ..bson import ObjectId
from .base import Database, Table

def is_match(lhs, rhs):
    """
    >>> is_match(12, 12)
    True
    >>> is_match(12, 13)
    False
    >>> is_match(11, {"$lt": 12})
    True
    >>> is_match(13, {"$lt": 12})
    False
    >>> is_match({"a1": 1, "a2": 2, "b3": 3}, {"$regex": "^a"})
    True
    >>> is_match({"a1": 1, "a2": 2, "b3": 3}, {"$regex": "^b"})
    True
    >>> is_match({"a1": 1, "a2": 2, "b3": 3}, {"$regex": "^c"})
    False
    """
    if isinstance(rhs, dict):
        matched = True
        for item in rhs:
            if item == "$regex":
                matched = any([key for key in lhs if re.match(rhs[item], key)])
            elif item == "$lt":
                matched = lhs < rhs[item]
            elif item == "$gt":
                matched = lhs > rhs[item]
            elif item == "$in":
                if isinstance(lhs, list):
                    matched = any([left for left in lhs if left in rhs[item]])
                else:
                    matched = lhs in rhs[item]
            else:
                raise Exception("unknown operator: %s" % item)
            if not matched:
                return False
        return matched
    else:
        if isinstance(lhs, list):
            if isinstance(rhs, list):
                return lhs == rhs
            else:
                return rhs in lhs
        else:
            return lhs == rhs

class ListTable(Table):
    def __init__(self, database=None, name=None, data=None):
        super().__init__(database, name)
        self.data = data or []

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def match(self, doc, query):
        """
        Does a dictionary match a (possibly-nested) query/dict?

        query is a dictionary of dotted words or query operations.

        >>> table = ListTable()
        >>> table.match({"x": 42}, {"x": 42})
        True
        >>> table.match({"x": 42}, {"x": 43})
        False
        >>> table.match({"x": {"y": 5}}, {"x.y": 5})
        True
        >>> table.match({"x": {"y": 5}}, {"x.y": 4})
        False
        >>> activity = {"name": "Joe"}
        >>> table.match(activity, {"$and": [{"name": "Sally"}, {"name": "Joe"}]})
        False
        >>> table.match(activity, {"$and": [{"name": "Joe"}, {"name": "Sally"}]})
        False
        >>> table.match(activity, {"$or": [{"name": "Sally"}, {"name": "Joe"}]})
        True
        >>> table.match(activity, {"$or": [{"name": "Joe"}, {"name": "Sally"}]})
        True
        """
        for item in query:
            if item == "$or":
                matched = False
                for each in query[item]:
                    if self.match(doc, each):
                        matched = True
                        break
                if not matched:
                    return False
            elif item == "$and":
                matched = True
                for each in query[item]:
                    if not self.match(doc, each):
                        matched = False
                        break
                if not matched:
                    return False
            else:
                thing = self.get_item_in_dict(doc, item)
                matched = is_match(thing, query[item])
                if not matched:
                    return False
        return True

    def get_item_in_dict(self, dictionary, item):
        """
        Get dictionary item from a dotted-word.

        >>> table = ListTable()
        >>> table.get_item_in_dict({"x": 1}, "x")
        1
        >>> table.get_item_in_dict({"x": {"y": 42}}, "x.y")
        42
        """
        current = dictionary
        for word in item.split("."):
            if word in current:
                current = current[word]
            else:
                return None
        return current

    def set_item_in_dict(self, dictionary, item, value, i=None):
        """
        Set dictionary item from a dotted-word.

        >>> table = ListTable()
        >>> d = {"x": 1}
        >>> table.get_item_in_dict(d, "x")
        1
        >>> table.set_item_in_dict(d, "x", 2)
        >>> table.get_item_in_dict(d, "x")
        2
        >>> d2 = {"x": {"y": 42}}
        >>> table.get_item_in_dict(d2, "x.y")
        42
        >>> table.set_item_in_dict(d2, "x.y", 43)
        >>> table.get_item_in_dict(d2, "x.y")
        43
        """
        current = dictionary
        words = item.split(".")
        for word in words[:-1]:
            current = current[word]
        current[words[-1]] = value
        ## update the database for those lists
        ## that are separate from the reference
        ## in dictionary (eg, redis)
        if i is not None:
            self.data[i] = dictionary

    def clear(self):
        self.data.clear()

    def sort(self, sort_key, sort_order):
        # sort_key = "_id"
        # sort_order = 1 or -1
        ## Always use ListTable here:
        return ListTable(data=sorted(
            self.data,
            key=lambda row: self.get_item_in_dict(row, sort_key),
            reverse=(sort_order == -1)))

    def insert_one(self, row):
        """
        >>> table = ListTable()
        >>> table.count()
        0
        >>> len(table.data)
        0
        >>> table.insert_one({"a": 1, "b": 2})
        >>> len(table.data)
        1
        >>> table.count()
        1
        >>> table.insert_one({"c": 1, "d": 2})
        >>> table.insert_one({"c": 1, "d": 2})
        >>> table.insert_one({"c": 1, "d": 3})
        >>> table.insert_one({"c": 1, "d": 3})
        >>> table.find({"a": 1}).count()
        1
        >>> table.find({"a": 2}).count()
        0
        >>> table.find({"b": 2}).count()
        1
        >>> table.find({"c": 1}).count()
        4
        >>> table.find({"c": 1, "d": 2}).count()
        2
        """
        row = copy.deepcopy(row) # expensive, but prevents errors
        if row.get("_id", None) is None:
            row["_id"] = ObjectId()
        self.data.append(row)

    def find(self, query=None, limit=None, enumerated=False):
        """
        >>> table = ListTable()
        >>> table.insert_one({"a": 1, "b": 2})
        >>> table.find({"a": 1}) # doctest: +ELLIPSIS
        [{'a': 1, 'b': 2, '_id': ObjectId('...')}]
        >>> table.find({"a": 2})
        []
        """
        if query is not None:
            if limit is not None:
                if enumerated:
                    return [(i,doc) for (i,doc) in enumerate(self.data) if self.match(doc, query)][:limit]
                else:
                    return ListTable(data=[doc for doc in self.data if self.match(doc, query)][:limit])
            else:
                if enumerated:
                    return [(i,doc) for (i,doc) in enumerate(self.data) if self.match(doc, query)]
                else:
                    return ListTable(data=[doc for doc in self.data if self.match(doc, query)])
        elif limit is not None:
            if enumerated:
                return list(enumerated(self.data[:limit]))
            else:
                return ListTable(data=self.data[:limit])
        else:
            if enumerated:
                return list(enumerated(self.data))
            else:
                return self

    def remove(self, query=None):
        """
        >>> table = ListTable()
        >>> table.insert_one({"a": 1, "b": 2})
        >>> table.insert_one({"c": 3, "d": 4})
        >>> table.find({"a": 1}) # doctest: +ELLIPSIS
        [{'a': 1, 'b': 2, '_id': ObjectId('...')}]
        >>> table.find({"a": 2})
        []
        >>> table.find({"d": 4}) # doctest: +ELLIPSIS
        [{'c': 3, 'd': 4, '_id': ObjectId('...')}]
        >>> table.remove({"d": 4})
        >>> table.find({"d": 4})
        []
        >>> table.find({"b": 2}) # doctest: +ELLIPSIS
        [{'a': 1, 'b': 2, '_id': ObjectId('...')}]
        """
        if query:
            items = [(i,doc) for (i,doc) in enumerate(self.data) if self.match(doc, query)]
            for i,doc in items:
                del self.data[i]
        else:
            self.data.clear()

    def find_one(self, query):
        """
        >>> table = ListTable()
        >>> table.insert_one({"a": 1, "b": 2})
        >>> table.insert_one({"a": 3, "b": 4})

        >>> table.find_one({"b": 2}) # doctest: +ELLIPSIS
        {'a': 1, 'b': 2, '_id': ObjectId('...')}
        >>> table.find_one({"b": 3})
        >>> table.find_one({"b": 4}) # doctest: +ELLIPSIS
        {'a': 3, 'b': 4, '_id': ObjectId('...')}
        """
        results = [doc for doc in self.data if self.match(doc, query)]
        if results:
            return results[0]
        else:
            return None

    def find_one_and_update(self, query, items, sort=None):
        one = self.find_one(query)
        if len(one) > 0:
            return False
        else:
            self.update_one(query, items)
            return True

    def update_one(self, query, items, upsert=False):
        results = [(i,doc) for (i,doc) in enumerate(self.data) if self.match(doc, query)]
        if len(results) > 0:
            self.process_updates(results[:1], items)
        elif upsert: ## update and insert
            self.insert_one(query)
            results = self.find(query, enumerated=True)
            self.process_updates(results, items)

    def process_updates(self, results, items):
        """
        results is rows of matched data (dicts)
        items are things like:

        * {'$set': {'meta.deleted': True}}
        * {'$set': {'meta.undo': True, 'meta.exta': 'object deleted'}}
        * {'$inc': {'meta.count_reply': -1, 'meta.count_direct_reply': -1}}

        >>> db = ListDatabase()
        >>> db.actors.insert_one({'meta': {'deleted': True}})
        >>> len(db.actors.find({'meta.deleted': True}))
        1
        >>> db.actors.process_updates(enumerate(db.actors.data),
        ...              {"$set": {'meta.deleted': False}})
        >>> len(db.actors.find({'meta.deleted': True}))
        0
        >>> len(db.actors.find({'meta.deleted': False}))
        1

        >>> db = ListDatabase()
        >>> db.actors.insert_one({'meta': {'count': 0}})
        >>> db.actors.find()[0]["meta"]["count"]
        0
        >>> db.actors.process_updates(enumerate(db.actors.data),
        ...              {"$inc": {'meta.count': +1}})
        >>> db.actors.find()[0]["meta"]["count"]
        1
        >>> db.actors.process_updates(enumerate(db.actors.data),
        ...              {"$inc": {'meta.count': +1}})
        >>> db.actors.find()[0]["meta"]["count"]
        2
        >>> db.actors.process_updates(enumerate(db.actors.data),
        ...              {"$inc": {'meta.count': -1}})
        >>> db.actors.find()[0]["meta"]["count"]
        1
        """
        for i,result in results:
            for item in items: # key
                if item == "$set":
                    for thing in items[item]: # keys of the $set
                        value = items[item][thing]
                        self.set_item_in_dict(result, thing, value, i)
                elif item == "$inc":
                    for thing in items[item]:
                        old_value = self.get_item_in_dict(result, thing)
                        incr = items[item][thing]
                        self.set_item_in_dict(result, thing, old_value + incr, i)

    def update(self, query, items, upsert=False):
        """
        >>> db = ListDatabase()
        >>> q = {"id": "XXX", "test": 42}
        >>> db.actors.update(q, {"$inc": {"test": +1}}, upsert=False)
        >>> len(db.actors.find(q))
        0
        >>> db.actors.update(q, {"$inc": {"test": +1}}, upsert=True)
        >>> len(db.actors.find(q))
        0
        >>> q = {"id": "XXX", "test": 43}
        >>> len(db.actors.find(q))
        1
        """
        results = [(i,doc) for (i,doc) in enumerate(self.data) if self.match(doc, query)]
        if len(results) > 0:
            self.process_updates(results, items)
        elif upsert: # update and insert
            self.insert_one(query)
            results = self.find(query, enumerated=True)
            self.process_updates(results, items)

    def count(self, query=None):
        if query:
            return len([doc for doc in self.data if self.match(doc, query)])
        else:
            return len(self.data)

    def count_documents(self, query):
        return self.count(query)

class ListDatabase(Database):
    Table = ListTable

"""
process_updates: [{'box': 'outbox', 'activity': {'type': 'Create', 'actor': 'http://localhost:5005', 'object': {'type': 'Note', 'sensitive': False, 'attributedTo': 'http://localhost:5005', 'cc': ['http://localhost:5005/followers'], 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'content': '<p>2</p>', 'tag': [], 'published': '2018-07-19T17:23:22Z', 'id': 'http://localhost:5005/outbox/75b40a6f5c319bdf/activity', 'url': 'http://localhost:5005/note/75b40a6f5c319bdf'}, '@context': ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1', {'Hashtag': 'as:Hashtag', 'sensitive': 'as:sensitive'}], 'published': '2018-07-19T17:23:22Z', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:5005/followers'], 'id': 'http://localhost:5005/outbox/75b40a6f5c319bdf'}, 'type': ['Create'], 'remote_id': 'http://localhost:5005/outbox/75b40a6f5c319bdf', 'meta': {'undo': False, 'deleted': False}, '_id': ObjectId('5b50c90a1342a3318e13d434'), '_requested': True}]

{'$set': {'meta.deleted': True}}

done! [{'box': 'outbox', 'activity': {'type': 'Create', 'actor': 'http://localhost:5005', 'object': {'type': 'Note', 'sensitive': False, 'attributedTo': 'http://localhost:5005', 'cc': ['http://localhost:5005/followers'], 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'content': '<p>2</p>', 'tag': [], 'published': '2018-07-19T17:23:22Z', 'id': 'http://localhost:5005/outbox/75b40a6f5c319bdf/activity', 'url': 'http://localhost:5005/note/75b40a6f5c319bdf'}, '@context': ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1', {'Hashtag': 'as:Hashtag', 'sensitive': 'as:sensitive'}], 'published': '2018-07-19T17:23:22Z', 'to': ['https://www.w3.org/ns/activitystreams#Public'], 'cc': ['http://localhost:5005/followers'], 'id': 'http://localhost:5005/outbox/75b40a6f5c319bdf'}, 'type': ['Create'], 'remote_id': 'http://localhost:5005/outbox/75b40a6f5c319bdf', 'meta': {'undo': False, 'deleted': False}, '_id': ObjectId('5b50c90a1342a3318e13d434'), '_requested': True, 'm': 'e'}]

process_updates: [] {'$set': {'meta.undo': True, 'meta.exta': 'object deleted'}}
done! []
"""
