from __future__ import annotations

import pytest

from pushup_page.strava_token import StravaTokenStore


def test_round_trip(tmp_path) -> None:
    token_path = tmp_path / "strava-token.enc"
    store = StravaTokenStore(token_path, "client-secret")

    store.save("refresh-token")

    assert store.load("stale-token") == "refresh-token"
    assert token_path.read_text(encoding="utf-8").strip() != "refresh-token"


def test_loads_fallback_when_token_file_is_missing(tmp_path) -> None:
    store = StravaTokenStore(tmp_path / "strava-token.enc", "client-secret")

    assert store.load("fallback-token") == "fallback-token"


def test_loads_fallback_when_client_secret_changes(tmp_path) -> None:
    token_path = tmp_path / "strava-token.enc"
    StravaTokenStore(token_path, "old-secret").save("old-token")

    store = StravaTokenStore(token_path, "new-secret")

    assert store.load("new-token") == "new-token"


def test_requires_a_refresh_token(tmp_path) -> None:
    store = StravaTokenStore(tmp_path / "strava-token.enc", "client-secret")

    with pytest.raises(RuntimeError, match="Missing Strava refresh token"):
        store.load()
