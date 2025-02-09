import hashlib
import json
import logging
import sqlite3
from pathlib import Path
from typing import Optional

all_files = []
logger = logging.getLogger()


class KVStorage:

    __minimal_version = 1
    __version = 1

    def __init__(self, file_name: str, table_name: str):
        """
        from https://stackoverflow.com/questions/47237807/use-sqlite-as-a-keyvalue-store
        """
        self.table_name = table_name
        self.path = Path(__file__).parent.parent / "cache" / file_name
        self.path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(
            f"Save {self.table_name} "
            f"in file {str(self.path.absolute())}, "
            f"file {'' if self.path.exists() else 'not '}exists"
        )

        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} (key text unique, value text)"
        )

    def load(self, key: str) -> Optional[str]:
        key_hash = self._get_hash(key)
        value = self.conn.execute(
            f"SELECT value FROM {self.table_name} WHERE key = ?", (key_hash,)
        ).fetchone()
        if value is None:
            return None
        data = json.loads(value[0])
        version = data.get("version", 0)
        if version < self.__minimal_version:
            return None
        return data["value"]

    def save(self, key: str, value: str):
        key_hash = self._get_hash(key)
        data = {"version": self.__version, "key": key, "value": value}
        data_json = json.dumps(data)
        self.conn.execute(
            f"REPLACE INTO {self.table_name} (key, value) VALUES (?,?)",
            (key_hash, data_json),
        )
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def _get_hash(self, key: str) -> str:
        return f"{hashlib.sha256(key.lower().encode()).hexdigest()}.json"
