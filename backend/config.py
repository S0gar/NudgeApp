from pathlib import Path
from dataclasses import dataclass

from configparser import ConfigParser

@dataclass(frozen=True)
class Directories:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_PATH = BASE_DIR / "config.ini"

@dataclass(frozen=True)
class Config:
    CONFIG = ConfigParser()
    _ = CONFIG.read(Directories.CONFIG_PATH)

    BOT_TOKEN = CONFIG["BOT setup"]["key"]

    DB_USER = CONFIG["DATABASE setup"]["DB_USER"]
    DB_PASS = CONFIG["DATABASE setup"]["DB_PASS"]
    DB_HOST = CONFIG["DATABASE setup"]["DB_HOST"]
    DB_PORT = CONFIG["DATABASE setup"]["DB_PORT"]
    DB_NAME = CONFIG["DATABASE setup"]["DB_NAME"]

    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
