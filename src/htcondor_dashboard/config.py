from __future__ import annotations

from functools import lru_cache

from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Class to hold the settings for the HTCondor Dashboard.
    Settings can be set via environment variables starting with HTDASH_.
    """

    exclude_submit_nodes: tuple[str] = ()  # type: ignore[assignment]
    model_config = SettingsConfigDict(env_prefix="HTDASH_")


@lru_cache
def get_settings() -> Settings:
    # os.environ['HTDASH_exclude_submit_nodes'] = '["status.dice.priv","submit-3"]'
    # os.environ['HTDASH_EXCLUDE_SUBMIT_NODES'] = '["status.dice.priv","submit-2"]'
    try:
        settings = Settings()
    except ValidationError as _:
        settings = Settings(exclude_submit_nodes=())  # type: ignore[arg-type]
    return settings


def get_template_dir() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")
