import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value

MYSQL_CONFIG = {
    "host": _require_env("DB_HOST"),
    "port": int(_require_env("DB_PORT")),
    "user": _require_env("DB_USER"),
    "password": _require_env("DB_PASSWORD"),
    "database" : _require_env("DB_NAME"),
    "cursorclass": pymysql.cursors.DictCursor
}

MONGO_URI = _require_env("MONGO_URI")