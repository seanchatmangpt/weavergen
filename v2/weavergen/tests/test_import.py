"""Test WeaverGen v2."""

import weavergen_v2


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(weavergen_v2.__name__, str)
