import uuid
from datetime import datetime

class Note:
    def __init__(self, content):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.content = content
        self.semantic_vector = None
        self.coordinates = None

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "content": self.content,
            "semantic_vector": self.semantic_vector,
            "coordinates": self.coordinates,
        }

    @classmethod
    def from_dict(cls, data_dict):
        note = cls(data_dict["content"])
        note.id = data_dict["id"]
        note.timestamp = data_dict["timestamp"]
        note.semantic_vector = data_dict.get("semantic_vector")
        note.coordinates = data_dict.get("coordinates")
        return note
