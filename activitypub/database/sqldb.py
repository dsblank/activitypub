
try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.pool import StaticPool
except:
    def create_engine(*args, **kwargs):
        raise Exception("You need to install sqlalchemy")

import logging
import json

from ..bson import ObjectId
from ..json import JSONDecoder, JSONEncoder
from .base import Database
from .listdb import ListTable

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
        if not self.database.table_exists(name):
            self.database.build_table(name)
        self.data = SQLList(database, name)

    def get_schema(self):
        ins = inspect(self.database.engine)
        return ins.get_columns(self.name)

    def get_columns(self):
        schema = self.get_schema()
        return [d["name"] for d in schema]

    def build_compare(self, lhs, rhs):
        if isinstance(rhs, dict):
            q = []
            for item in rhs:
                if item == "$regex":
                    q.append("SQL regex") ## FIXME
                elif item == "$lt":
                    q.append("(%s < %s)" % (lhs, rhs[item]))
                elif item == "$gt":
                    q.append("(%s > %s)" % (lhs, rhs[item]))
                elif item == "$in":
                    if isinstance(lhs, list):
                        q.append("(%s IN %s)" % (lhs, rhs)) ## FIXME?
                    else:
                        q.append("(%s IN %s)" % (lhs, rhs[item])) ## FIXME?
                else:
                    raise Exception("unknown operator: %s" % item)
            return "(" + (" AND ".join(q)) + ")"
        else:
            if isinstance(lhs, list):
                if isinstance(rhs, list):
                    return "(%s = %s)" % (lhs, repr(rhs)) ## FIXME?
                else:
                    return "(%s IN %s)" % (rhs, lhs) ## FIXME?
            else:
                return "(%s = %s)" % (lhs, repr(rhs))

    def build_query(self, query, limit=None):
        q = []
        for item in query:
            if item == "$or":
                expr = "(" + (" OR ".join([self.build_query(each) for each in query[item]])) + ")"
            elif item == "$and":
                expr = "(" + (" AND ".join([self.build_query(each) for each in query[item]])) + ")"
            else:
                expr = self.build_compare(item, query[item])
            q.append(expr)
        return "(" + (" AND ".join(q)) + ")"

    def find(self, query=None, limit=None, enumerated=False):
        ## if the query contains a SQL table field, then
        ## use that portion
        ## WIP: find portion of query that can be SQL selected
        ## NOTE: limit can only be applied if full query applies
        # logging.info("query: %s" % query)
        # if query is not None or limit is not None:
        #     q = self.build_query(query, limit)
        #     logging.info("built q: %s" % q)
        #     if False: ## TODO: handle query
        #         results = self.database.execute(q)
        #         return ListTable(data=results.fetchall()).find(query, enumerated=enumerated)
        ## else, just go through all of the items
        return super().find(query, limit, enumerated)

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
        super().__init__()
        args = list(args)
        if args[0].endswith(":memory:"):
            args[0] = args[0].replace(":memory:", "")
        if args[0] == "sqlite://": # in-memory
            kwargs.update({
                "connect_args": {'check_same_thread': False},
                "poolclass": StaticPool,
            })
            self.engine = create_engine(*args, **kwargs)
            self.session = sessionmaker(bind=self.engine)()
        else:
            self.engine = create_engine(*args, **kwargs)
            self.session = scoped_session(sessionmaker(bind=self.engine))

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def execute(self, *args, **kwargs):
        return self.session.execute(*args, **kwargs)

    def table_exists(self, table):
        ins = inspect(self.engine)
        return table in ins.get_table_names()

    def build_table(self, name):
        try:
            self.execute(
                """CREATE TABLE %s (
                    rowid INTEGER PRIMARY KEY ASC,
                    oid CHAR(24),
                    blob_data BLOB
                )""" % name)
            self.commit()
        except:
            self.rollback()
            raise
