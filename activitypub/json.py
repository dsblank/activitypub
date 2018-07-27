import json
from .bson import ObjectId

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
