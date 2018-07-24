try:
    import redis
    from redis_collections import List
    from_url = redis.StrictRedis.from_url
except:
    def from_url(*args, **kwargs):
        raise Exception("You need to install redis and redis_collections")

from .listdb import ListTable
from .base import Database

class RedisTable(ListTable):
    def __init__(self, database=None, name=None, data=None):
        super().__init__(database, name)
        self.data = List(key=name, data=data, redis=self.database.redis)

class RedisDatabase(Database):
    Table = RedisTable
    def __init__(self, url=None, **kwargs):
        """
        url
        * "redis://localhost:6379"
        * "redis://localhost:6379/0"
        """
        self.redis = from_url(url, **kwargs) if url else None
        super().__init__()
