
from activitypub.database import *
from activitypub.manager import Manager

def test_all():
    for db in [
            ListDatabase(),
            SQLDatabase("sqlite://"),
            SQLDatabase("sqlite:///sqlite.db"),
            MongoDatabase("mongodb://localhost:27017", "dsblank_localhost:5005"),
            RedisDatabase("redis://localhost:6379/0"),
    ]:
        print("Testing", db.__class__.__name__, "...")
        manager = Manager(database=db)
        if manager.database.table_exists("activities"):
            manager.database.activities.clear()
        else:
            manager.database.build_table("activities")
        manager.database.activities.clear()
        manager.database.actors.clear()

        assert manager.database.actors.count_documents(
            {"$or": [{'id': 'https://example.com/alyssa'},
                     {'id': 'https://example.com/alyssa'}]}) == 0
        assert manager.database.actors.count_documents(
            {"$or": [{'id': 'https://example.com/alyssa'},
                     {'id': 'https://example.com/alyssa'}]}) == 0

        p1 = manager.Person(id="alyssa")
        p2 = manager.Person(id="brenda")

        manager.database.actors.insert_one(p1.to_dict())
        manager.database.actors.insert_one(p2.to_dict())

        assert manager.database.actors.count_documents(
            {"$or": [{'id': 'https://example.com/alyssa'},
                     {'id': 'https://example.com/brenda'}]}) == 2
        assert len(list(manager.database.actors.find(
            {"$or": [{'id': 'https://example.com/alyssa'},
                     {'id': 'https://example.com/brenda'}]}))) == 2

        assert manager.database.actors.count_documents(
            {'id': 'https://example.com/alyssa'}) == 1
        assert manager.database.actors.count_documents({}) == 2

        ## Clean up
        manager.database.activities.clear()
        manager.database.actors.clear()

if __name__ == "__main__":
    test_all()
