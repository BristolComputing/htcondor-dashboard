from __future__ import annotations

from functools import lru_cache
from typing import Tuple, Union

from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

ListSetting = Union[Tuple[str], Tuple[()]]


class Settings(BaseSettings):
    """
    Class to hold the settings for the HTCondor Dashboard.
    Settings can be set via environment variables starting with HTDASH_.
    """

    exclude_submit_nodes: ListSetting
    model_config = SettingsConfigDict(env_prefix="HTDASH_")


@lru_cache
def get_settings() -> Settings:
    """Cached function to get the settings for the HTCondor Dashboard.
    Sets defaults if the settings are not found.
    """
    # os.environ['HTDASH_exclude_submit_nodes'] = '["status.dice.priv","submit-3"]'
    try:
        settings = Settings()  # type: ignore[call-arg]
    except ValidationError as _:
        settings = Settings(exclude_submit_nodes=())
    return settings


def get_template_dir() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")
