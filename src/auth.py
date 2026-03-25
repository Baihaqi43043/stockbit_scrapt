import json
import time
import httpx
from pathlib import Path
import config

TOKEN_FILE = Path(__file__).parent.parent / ".token_cache.json"


def _save_token(data: dict):
    TOKEN_FILE.write_text(json.dumps(data))


def _load_token() -> dict:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return {}


def _is_expired(token_data: dict, buffer_seconds: int = 300) -> bool:
    """Anggap expired kalau sudah lewat dari (expires_at - buffer)."""
    expires_at = token_data.get("expires_at", 0)
    return time.time() >= (expires_at - buffer_seconds)


def login() -> dict:
    """Login ke Stockbit, return token data."""
    payload = {
        "player_id": config.STOCKBIT_PLAYER_ID,
        "user":      config.STOCKBIT_USERNAME,
        "password":  config.STOCKBIT_PASSWORD,
    }
    with httpx.Client(headers=config.DEFAULT_HEADERS, timeout=30) as client:
        resp = client.post(config.LOGIN_URL, json=payload)
        resp.raise_for_status()
        body = resp.json()

    data = body.get("data", {})
    access  = data.get("access",  {})
    refresh = data.get("refresh", {})

    token_data = {
        "access_token":  access.get("token", ""),
        "refresh_token": refresh.get("token", ""),
        # Stockbit tidak kirim expires_in, asumsi 24 jam
        "expires_at": time.time() + 86400,
    }
    _save_token(token_data)
    print("[auth] Login berhasil.")
    return token_data


def refresh_token(token_data: dict) -> dict:
    """Refresh access token pakai refresh_token."""
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token_data['refresh_token']}"}
    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.post(config.REFRESH_URL)

    if resp.status_code == 401:
        print("[auth] Refresh token expired, login ulang...")
        return login()

    resp.raise_for_status()
    body = resp.json()
    data    = body.get("data", {})
    access  = data.get("access",  {})
    refresh = data.get("refresh", {})

    token_data["access_token"]  = access.get("token",  token_data["access_token"])
    token_data["refresh_token"] = refresh.get("token", token_data["refresh_token"])
    token_data["expires_at"]    = time.time() + 86400
    _save_token(token_data)
    print("[auth] Token diperbarui.")
    return token_data


def get_valid_token() -> str:
    """
    Return access_token yang valid.
    Auto-refresh jika hampir expired, auto-login jika tidak ada cache.
    """
    token_data = _load_token()

    if not token_data or not token_data.get("access_token"):
        token_data = login()
    elif _is_expired(token_data):
        token_data = refresh_token(token_data)

    return token_data["access_token"]
