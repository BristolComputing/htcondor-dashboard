from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from pydantic_settings.sources import SettingsError

from htcondor_dashboard.config import Settings, get_settings


def test_default_settings():
    settings = get_settings()
    assert settings.grafana_url == "http://localhost:3000"
    assert settings.htcondor_ce_view_url == "http://example_ce"
    assert settings.exclude_submit_nodes == ()
    get_settings.cache_clear()


def test_custom_settings():
    with patch.dict(
        os.environ,
        {
            "HTDASH_GRAFANA_URL": "http://custom_grafana",
            "HTDASH_HTCONDOR_CE_VIEW_URL": "http://custom_ce",
            "HTDASH_EXCLUDE_SUBMIT_NODES": '["node1","node2"]',
        },
    ):
        settings = get_settings()
    assert settings.grafana_url == "http://custom_grafana"
    assert settings.htcondor_ce_view_url == "http://custom_ce"
    assert settings.exclude_submit_nodes == ("node1", "node2")
    get_settings.cache_clear()


def test_invalid_settings():
    with patch.dict(
        os.environ,
        {
            "HTDASH_EXCLUDE_SUBMIT_NODES": "invalid_value",
        },
    ), pytest.raises(SettingsError):
        Settings()
