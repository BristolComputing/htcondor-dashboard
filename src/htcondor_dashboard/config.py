from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Class to hold the settings for the HTCondor Dashboard.
    Settings can be set via environment variables starting with HTDASH_.
    """

    exclude_submit_nodes: tuple[str, ...] = ()
    grafana_url: str = "http://localhost:3000"
    htcondor_ce_view_url: str = "http://example_ce"
    report_path: Path | None = None
    model_config = SettingsConfigDict(env_prefix="HTDASH_")


@lru_cache
def get_settings() -> Settings:
    """Cached function to get the settings for the HTCondor Dashboard.
    Sets defaults if the settings are not found.
    """
    try:
        settings = Settings()
    except ValidationError as _:
        settings = Settings(exclude_submit_nodes=())
    return settings


def get_template_dir() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")
