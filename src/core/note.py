import uuid
from datetime import datetime

class Note:
    def __init__(self, content, id=None, embedding=None, position=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat() # Consider if timestamp should also come from dict in from_dict
        self.content = content
        self.embedding = embedding
        self.position = position

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "content": self.content,
            "embedding": self.embedding,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data_dict):
        note = cls(
            content=data_dict["content"],
            id=data_dict.get("id"), # Pass ID to constructor
            embedding=data_dict.get("embedding"), # Renamed from semantic_vector
            position=data_dict.get("position") # Renamed from coordinates
        )
        # Timestamp handling: if it's in dict, use it, otherwise constructor sets it.
        if "timestamp" in data_dict:
            note.timestamp = data_dict["timestamp"]
        return note
