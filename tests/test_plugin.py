"""Tests for the pytest plugin registration."""

import pytest


def test_plugin_markers(pytestconfig):
    """Verify proofagent markers are registered."""
    markers = pytestconfig.getini("markers")
    marker_names = [m.split(":")[0].strip() for m in markers]
    assert "proofagent" in marker_names
    assert "safety" in marker_names
    assert "agent" in marker_names
