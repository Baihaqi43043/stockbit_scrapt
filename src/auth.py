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
    expires_at = token_data.get("expires_at", 0)
    return time.time() >= (expires_at - buffer_seconds)


def _is_valid_jwt(token: str) -> bool:
    """Cek apakah token adalah JWT (bukan UUID pendek dari new_device flow)."""
    return token and len(token) > 40 and "." in token


def login_via_browser() -> dict:
    """Login pakai Playwright browser, return token data."""
    from src.token_fetcher import fetch_token_via_browser
    access_token = fetch_token_via_browser(headless=False)
    token_data = _load_token()  # token_fetcher sudah simpan ke file
    return token_data


def refresh_token(token_data: dict) -> dict:
    """Refresh access token pakai refresh_token."""
    refresh = token_data.get("refresh_token", "")
    if not refresh:
        print("[auth] Tidak ada refresh token, login ulang via browser...")
        return login_via_browser()

    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {refresh}"}
    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.post(config.REFRESH_URL)

    if resp.status_code == 401:
        print("[auth] Refresh token expired, login ulang via browser...")
        return login_via_browser()

    resp.raise_for_status()
    body = resp.json()
    data       = body.get("data", {})
    new_access  = data.get("access",  {}).get("token", "")
    new_refresh = data.get("refresh", {}).get("token", "")

    if new_access:
        token_data["access_token"]  = new_access
        token_data["refresh_token"] = new_refresh or refresh
        token_data["expires_at"]    = time.time() + 86400
        _save_token(token_data)
        print("[auth] Token diperbarui.")

    return token_data


def get_valid_token() -> str:
    """
    Return access_token yang valid.
    - Kalau tidak ada cache → browser login
    - Kalau hampir expired → coba refresh, fallback browser login
    """
    token_data = _load_token()

    if not token_data or not token_data.get("access_token"):
        print("[auth] Belum ada token, membuka browser untuk login...")
        token_data = login_via_browser()
    elif _is_expired(token_data):
        print("[auth] Token expired, mencoba refresh...")
        token_data = refresh_token(token_data)

    access = token_data.get("access_token", "")
    if not access:
        raise RuntimeError("[auth] Gagal mendapatkan token yang valid.")

    return access
