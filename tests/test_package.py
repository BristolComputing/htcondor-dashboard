from __future__ import annotations

import importlib.metadata

import htcondor_dashboard as m


def test_version():
    assert importlib.metadata.version("htcondor_dashboard") == m.__version__
