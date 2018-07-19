from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

class Application():
    def __init__(self, engine_string):
        self.engine = create_engine(engine_string)
        Base.metadata.create_all(self.engine)
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
