from typing import List

from pydantic import BaseModel
from telegram import MessageEntity

from schemas.message_type import MessageType


class Entity(BaseModel):
    message_type: MessageType
    offset: int
    length: int

    def to_tg(self) -> MessageEntity:
        return MessageEntity(
            type=self.message_type.value, offset=self.offset, length=self.length
        )

    @staticmethod
    def from_tg(entity: MessageEntity) -> "Entity":
        return Entity(
            message_type=MessageType(entity.type),
            offset=entity.offset,
            length=entity.length,
        )


class CachedMessage(BaseModel):
    text: str
    entities: List[Entity]

    def tg_entities(self) -> List[MessageEntity]:
        return [_.to_tg() for _ in self.entities]
