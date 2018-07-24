import json

from ..bson import ObjectId
from .base import Database
from .listdb import ListTable

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return {"$oid": str(o)}
        return super().default(o)

class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '$oid' not in obj:
            return obj
        return ObjectId(obj['$oid'])

class SQLList():
    def __init__(self, database, name):
        self.database = database
        self.name = name

    def __getitem__(self, item):
        if isinstance(item, int):
            result = self.database.execute(
                """SELECT blob_data FROM %s WHERE rowid = :rowid"""
                % (self.name), {"rowid": item})
            item = result.fetchone()
            if item:
                item = json.loads(item[0], cls=JSONDecoder)
        elif isinstance(item, slice):
            items = [item in islice(self, item.start, item.stop, item.step)]
            return items
        if item:
            return item
        else:
            raise IndexError("list index out of range")

    def __setitem__(self, item, value):
        s = json.dumps(value, cls=JSONEncoder)
        # first see if it exists:
        try:
            old_item = self[item]
        except:
            old_item = None
        if old_item:
            # update it
            try:
                self.database.execute(
                    """UPDATE %s SET blob_data = :s WHERE rowid = :rowid;"""
                    % (self.name), {"s": s, "rowid": item})
                self.database.commit()
            except:
                self.database.rollback()
                raise
        else:
            # insert it
            oid = str(value["_id"])
            try:
                self.database.execute(
                    """INSERT INTO %s (blob_data, oid, rowid) VALUES (:s, :oid, :rowid);"""
                    % (self.name), {"s": s, "rowid": item, "oid": oid})
                self.database.commit()
            except:
                self.database.rollback()
                raise

    def __delitem__(self, key):
        try:
            self.database.execute(
                """DELETE FROM %s WHERE rowid = :rowid;"""
                % (self.name), {"rowid": key})
            self.database.execute(
                """UPDATE %s SET rowid = (rowid - 1) WHERE rowid > :rowid;"""
                % self.name, {"rowid": key})
            self.database.commit()
        except:
            self.database.rollback()
            raise

    def clear(self):
        try:
            self.database.execute("DELETE from %s;" % self.name)
            self.database.commit()
        except:
            self.database.rollback()
            raise

    def append(self, item):
        pos = len(self)
        self[pos] = item

    def __len__(self):
        result = self.database.execute("SELECT count(1) FROM %s" % self.name)
        row = result.fetchone()
        return row[0]

class SQLTable(ListTable):
    def __init__(self, database, name):
        super().__init__(database, name)
        if not self.table_exists(name):
            self.build_table(name)
        self.data = SQLList(database, name)

    def table_exists(self, table):
        result = self.database.execute("""SELECT COUNT(*) 
                                           FROM sqlite_master 
                                           WHERE type='table' AND name='%s';""" % table)
        return result.fetchone()[0] != 0

    def build_table(self, name):
        try:
            self.database.execute(
                """CREATE TABLE %s (
                    rowid INTEGER PRIMARY KEY ASC,
                    oid CHAR(24),
                    blob_data BLOB
                )""" % name)
            self.database.commit()
        except:
            self.database.rollback()
            raise

    def sort(self, sort_key, sort_order):
        # sort_key = "_id"
        # sort_order = 1 or -1
        ## Always use ListTable here:
        return ListTable(data=sorted(
            self.data,
            key=lambda row: self.get_item_in_dict(row, sort_key),
            reverse=(sort_order == -1)))

class SQLDatabase(Database):
    Table = SQLTable
    
    def __init__(self, *args, **kwargs):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        #from sqlalchemy.pool import StaticPool
        #from sqlalchemy.pool import QueuePool

        super().__init__()
        self.engine = create_engine(*args, **kwargs)
        # poolclass=QueuePool,
        # convert_unicode=True,
        # connect_args={'check_same_thread':False},
        # poolclass=StaticPool,
        self.session = scoped_session(sessionmaker(bind=self.engine))
        
    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def execute(self, *args, **kwargs):
        return self.session.execute(*args, **kwargs)

