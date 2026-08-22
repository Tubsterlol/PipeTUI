from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models import Base


class Database:

    def __init__(self, database_url="sqlite:///devops.db"):

        self.engine = create_engine(database_url)

        self.Session = sessionmaker(
            bind=self.engine
        )

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close(self):
        self.engine.dispose()