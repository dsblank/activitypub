from pymongo import MongoClient

from .base import Database, Table

class MongoTable(Table):
    """
    """
    def __init__(self, database, name):
        super().__init__(database, name)
        self.collection = getattr(database.DB, name)

    def __getattr__(self, attr):
        if "collection" in self.__dict__:
            return getattr(self.collection, attr)
        else:
            raise AttributeError("no such attribute: %s" % attr)

    def __setattr__(self, attr, value):
        if "collection" in self.__dict__ and hasattr(self.collection, attr):
            setattr(self.collection, attr, value)
        else:
            self.__dict__[attr] = value

class MongoDatabase(Database):
    def __init__(self, uri, db_name):
        self.uri = uri
        self.client = MongoClient(self.uri)
        self.db_name = db_name
        self.DB = self.client[self.db_name]
        super().__init__(MongoTable)
