from schemas.message_type import MessageType


class Chunk:

    def __init__(self, message: str):
        assert len(message) > 0
        self.message = message
        text = message.strip()
        if text.startswith("**"):
            self.message_type = MessageType.BOLD.value
        elif text.startswith("Synonyms"):
            self.message_type = MessageType.ITALIC.value
        elif text.startswith("<RUS>"):
            self.message = message.replace("<RUS>", "")
            self.message_type = MessageType.SPOILER.value
        else:
            self.message_type = ""
