from __future__ import annotations

import base64
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

TOKEN_KEY_INFO = b"pushup-page:strava-refresh-token:v1"


class StravaTokenStore:
    def __init__(self, path: Path, client_secret: str) -> None:
        self.path = path
        self._fernet = Fernet(self._derive_key(client_secret))

    @staticmethod
    def _derive_key(client_secret: str) -> bytes:
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=TOKEN_KEY_INFO,
        ).derive(client_secret.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    def load(self, fallback_token: str | None = None) -> str:
        if self.path.exists():
            encrypted_token = self.path.read_bytes().strip()
            try:
                return self._fernet.decrypt(encrypted_token).decode("utf-8")
            except (InvalidToken, ValueError):
                if fallback_token:
                    print(
                        "Stored Strava refresh token could not be decrypted; "
                        "using the configured fallback token."
                    )
                else:
                    raise RuntimeError(
                        "Stored Strava refresh token could not be decrypted. "
                        "Update CLIENT_SECRET and REFRESH_TOKEN, or remove the "
                        "encrypted token file to bootstrap it again."
                    ) from None

        if fallback_token:
            return fallback_token

        raise RuntimeError(
            "Missing Strava refresh token. Configure REFRESH_TOKEN or provide a "
            "decryptable encrypted token file."
        )

    def save(self, refresh_token: str) -> None:
        encrypted_token = self._fernet.encrypt(refresh_token.encode("utf-8"))
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temporary_path.write_bytes(encrypted_token + b"\n")
        temporary_path.replace(self.path)
