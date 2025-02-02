import logging
from enum import Enum
from pathlib import Path
from typing import Iterable, Tuple

from llm_model import Model

logger = logging.getLogger(__name__)


class Chunk:

    def __init__(self, message: str, message_type: str):
        assert len(message) > 0
        self.message = message
        self.message_type = message_type


class Handler:

    def __init__(self, model: Model) -> None:
        self.model = model
        self._cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        self._latin = "abcdefghijklmnopqrstuvwxyz"
        self._templates = Path(__file__).parent / "resources"
        assert self._templates.is_dir()

    def handle(self, message: str) -> Iterable[Chunk]:
        if len(message) == 0:
            return

        latin_cnt, cyrillic_cnt, word_cnt = self._cnt_letters(message)

        if cyrillic_cnt > latin_cnt:
            logger.info("Assume need translate from russian to english")
            yield from self._translate_ru_en(message)
        elif word_cnt >= 5:
            logger.info("Assume need to check grammar")
            yield from self._check_grammar(message)
        else:
            logger.info("Assume need translate from english to russian")
            yield from self._translate_en_ru(message)

    @staticmethod
    def _batch(stream: Iterable[str], max_len: int = 30) -> Iterable[str]:
        batch = ""
        for chunk in stream:
            batch += chunk
            if len(batch) > max_len:
                yield batch
                batch = ""
        if len(batch) > 0:
            yield batch

    def _cnt_letters(self, message: str) -> Tuple[int, int, int]:
        message = message.lower()
        word_cnt = len(message.strip().split())
        if len(message) == 0:
            return 0, 0, 0
        latin_cnt = sum(letter in self._latin for letter in message)
        cyrillic_cnt = sum(letter in self._cyrillic for letter in message)
        return latin_cnt, cyrillic_cnt, word_cnt

    @staticmethod
    def from_env() -> "Handler":
        model = Model.from_env()
        return Handler(model)

    def _check_grammar(self, message: str) -> Iterable[Chunk]:
        with open(self._templates / "check_grammar.txt") as f:
            template = f.read()
        prompt = template.format(message=message)
        yield from (Chunk(text, "") for text in self._batch(self.model.invoke(prompt)) if len(text) > 0)

    def _translate_en_ru(self, message: str):
        with open(self._templates / "translate_en_ru.txt") as f:
            template = f.read()
        prompt = template.format(message=message)
        yield from (Chunk(text, "") for text in self._batch(self.model.invoke(prompt)) if len(text) > 0)

    def _translate_ru_en(self, message: str):
        with open(self._templates / "translate_ru_en.txt") as f:
            template = f.read()
        prompt = template.format(message=message)
        yield from (Chunk(text, "") for text in self._batch(self.model.invoke(prompt)) if len(text) > 0)
