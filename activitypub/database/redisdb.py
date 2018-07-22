from redis_collections import List
from .dummy import DummyTable
from .base import Database

class RedisTable(DummyTable):
    def __init__(self, database=None, name=None, data=None):
        super().__init__(database, name)
        self.data = List(key=name, data=data)

class RedisDatabase(Database):
    def __init__(self):
        super().__init__(RedisTable)
