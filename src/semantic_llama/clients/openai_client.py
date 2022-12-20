import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import openai
from oaklib.utilities.apikey_manager import get_apikey_value


@dataclass
class OpenAIClient:
    max_tokens: int = field(default_factory=lambda: 3000)
    engine: str = field(default_factory=lambda: "text-davinci-003")
    cache_db_path: str = None
    api_key: str = None

    def __post_init__(self):
        self.api_key = get_apikey_value("openai")
        openai.api_key = self.api_key

    def complete(self, prompt, **kwargs) -> str:
        engine = self.engine
        cur = self.db_connection()
        res = cur.execute("SELECT payload FROM cache WHERE prompt=? AND engine=?", (prompt, engine))
        payload = res.fetchone()
        if payload:
            print(f"Using cached payload for prompt: {prompt}")
            return payload[0]
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=self.max_tokens,
            **kwargs,
        )
        payload = response.choices[0].text
        print(f"Storing payload of len: {len(payload)}")
        cur.execute(
            "INSERT INTO cache (prompt, engine, payload) VALUES (?, ?, ?)",
            (prompt, engine, payload),
        )
        cur.connection.commit()
        return payload

    def db_connection(self):
        if not self.cache_db_path:
            self.cache_db_path = ".openai_cache.db"
        print(f"Caching OpenAI responses to {self.cache_db_path}")
        create = not Path(self.cache_db_path).exists()
        con = sqlite3.connect(self.cache_db_path)
        cur = con.cursor()
        if create:
            cur.execute("CREATE TABLE cache (prompt, engine, payload)")
        return cur
