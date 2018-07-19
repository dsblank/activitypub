class Database():
    """
    Base database class.
    """
    def __init__(self, Table):
        self.activities = Table(self, "activities")
        self.u2f = Table(self, "u2f")
        self.instances = Table(self, "instances")
        self.actors = Table(self, "actors")
        self.indieauth = Table(self, "indieauth")

    ## TODO: put required methods to override here

class Table():
    """
    Base table class.
    """
    def __init__(self, database=None, name=None):
        self.database = database
        self.name = name

    ## TODO: put required methods to override here
