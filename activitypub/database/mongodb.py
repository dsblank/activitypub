try:
    from pymongo import MongoClient
except:
    def MongoClient(*args, **kwargs):
        raise Exception("You need to install pymongo")

from .base import Database, Table

class Log():
    """
    For debugging only. See below.
    """
    def __init__(self, item):
        self.__dict__["item"] = item

    def __getattr__(self, attr):
        return getattr(self.item, attr)

    def __setattr__(self, attr, value):
        setattr(self.item, attr, value)

    def __call__(self, *args, **kwargs):
        print("calling:", self.item, args, kwargs)
        result = self.item(*args, **kwargs)
        print("result:", result)
        return result

class MongoTable(Table):
    """
    """
    def __init__(self, database, name):
        super().__init__(database, name)
        self.collection = getattr(database.DB, name)

    def __getattr__(self, attr):
        if "collection" in self.__dict__:
            #return Log(getattr(self.collection, attr))
            return getattr(self.collection, attr)
        else:
            raise AttributeError("no such attribute: %s" % attr)

    def __setattr__(self, attr, value):
        if "collection" in self.__dict__ and hasattr(self.collection, attr):
            setattr(self.collection, attr, value)
        else:
            self.__dict__[attr] = value

    def clear(self):
        self.collection.drop()

class MongoDatabase(Database):
    Table = MongoTable
    def __init__(self, uri, db_name):
        super().__init__()
        self.uri = uri
        self.client = MongoClient(self.uri)
        self.db_name = db_name
        self.DB = self.client[self.db_name]

    def table_exists(self, table):
        return table in self.client.database_names()
