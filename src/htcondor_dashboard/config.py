from __future__ import annotations

from functools import lru_cache

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    exclude_submit_nodes: list[str] = []
    model_config = SettingsConfigDict(env_prefix="HTDASH_")


@lru_cache
def get_settings():
    # os.environ['HTDASH_exclude_submit_nodes'] = '["status.dice.priv","submit-3"]'
    # os.environ['HTDASH_EXCLUDE_SUBMIT_NODES'] = '["status.dice.priv","submit-2"]'
    try:
        settings = Settings()
    except Exception as _:
        settings = Settings(exclude_submit_nodes=[])
    return settings


def get_template_dir():
    return Jinja2Templates(directory="templates")
