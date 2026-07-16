from __future__ import annotations

import datetime as dt

import pytest

from pushup_page import strava_sync
from pushup_page.strava_token import StravaTokenStore


def test_persists_rotated_token_when_sync_fails(monkeypatch, tmp_path) -> None:
    class FakeGenerator:
        instance = None

        def __init__(self, db_path: str) -> None:
            self.access_token = ""
            self.refresh_token = ""
            self.closed = False
            FakeGenerator.instance = self

        def set_strava_config(
            self, client_id: str, client_secret: str, refresh_token: str
        ) -> None:
            self.refresh_token = refresh_token

        def sync(self, force: bool, start_date: dt.datetime | None = None) -> None:
            self.access_token = "access-token"
            self.refresh_token = "rotated-token"
            raise RuntimeError("activity sync failed")

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(strava_sync, "Generator", FakeGenerator)
    token_store = StravaTokenStore(tmp_path / "strava-token.enc", "client-secret")

    with pytest.raises(RuntimeError, match="activity sync failed"):
        strava_sync.run_strava_sync(
            client_id="client-id",
            client_secret="client-secret",
            refresh_token="initial-token",
            start_date=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
            export_csv=False,
            token_store=token_store,
        )

    assert FakeGenerator.instance is not None
    assert FakeGenerator.instance.closed
    assert token_store.load() == "rotated-token"
