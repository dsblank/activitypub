class Table():
    """
    Base table class.
    """
    def __init__(self, database=None, name=None):
        self.database = database
        self.name = name

class Database():
    """
    Base database class.
    """
    Table = Table
    def __init__(self):
        self._tables = {}

    def __getattr__(self, attr):
        if attr not in self._tables:
            self._tables[attr] = self.Table(self, attr)
        return self._tables[attr]

    def table_exists(self, table):
        return table in self._tables

    def build_table(self, name):
        self._tables[name] = self.Table(self, name)

