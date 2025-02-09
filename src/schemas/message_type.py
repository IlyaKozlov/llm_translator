from enum import Enum


class MessageType(str, Enum):
    BOLD = "bold"
    SPOILER = "spoiler"
    ITALIC = "italic"
