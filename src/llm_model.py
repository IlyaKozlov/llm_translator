import os
from typing import Iterable
from langchain_openai import ChatOpenAI


class Model:

    def __init__(self, api_key: str) -> None:
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    def invoke(self, prompt: str) -> Iterable[str]:
        for chunk in self.llm.stream(prompt):
            yield chunk.content

    @staticmethod
    def from_env():
        api_key = os.getenv("LLM_API_KEY")
        return Model(api_key=api_key)
