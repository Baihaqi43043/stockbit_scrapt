"""
Ambil Bearer token Stockbit dari session Chrome yang sudah login.

Cara kerja:
- Pakai Chrome profile yang sudah login (Profile 7 = baihaqi43043@gmail.com)
- Buka stockbit.com/stream
- Intercept request ke exodus.stockbit.com → tangkap Authorization header
- Simpan token ke .token_cache.json

PENTING: Tutup Chrome dulu sebelum jalankan script ini.
"""

import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent.parent))

TOKEN_FILE       = Path(__file__).parent.parent / ".token_cache.json"
CHROME_USER_DATA = "/Users/rsudbireuen/Library/Application Support/Google/Chrome"
CHROME_PROFILE   = "Profile 7"  # baihaqi43043@gmail.com
TARGET_URL       = "https://stockbit.com/stream"
TRIGGER_DOMAIN   = "exodus.stockbit.com"


def _save_token(access_token: str, refresh_token: str = ""):
    data = {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "expires_at":    time.time() + 86400,
    }
    TOKEN_FILE.write_text(json.dumps(data))
    print(f"[token_fetcher] Token disimpan.")


def fetch_token_via_browser(headless: bool = False) -> str:
    """
    Buka Chrome dengan profile yang sudah login, intercept token dari request.
    Return access_token string.
    """
    captured = {"token": None, "refresh": None}

    with sync_playwright() as p:
        # Pakai persistent context = pakai session Chrome yang sudah ada
        context = p.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA,
            channel="chrome",           # pakai Chrome yang terinstall, bukan Chromium
            headless=headless,
            args=[
                f"--profile-directory={CHROME_PROFILE}",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        page = context.new_page()

        def on_request(request):
            if TRIGGER_DOMAIN in request.url and captured["token"] is None:
                auth = request.headers.get("authorization", "")
                if auth.startswith("Bearer ") and len(auth) > 30:
                    token = auth.replace("Bearer ", "").strip()
                    captured["token"] = token
                    print(f"[token_fetcher] Token tertangkap dari: {request.url[:70]}")
                    print(f"[token_fetcher] Token: {token[:16]}...")

        page.on("request", on_request)

        # Tunggu page pertama siap, baru navigate
        time.sleep(3)

        print(f"[token_fetcher] Navigasi ke {TARGET_URL}...")
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"[token_fetcher] Halaman terbuka: {page.url}")
        except Exception as e:
            print(f"[token_fetcher] goto error: {e}, coba lanjut...")

        # Tunggu sampai token tertangkap (max 30 detik)
        waited = 0
        while captured["token"] is None and waited < 30:
            time.sleep(1)
            waited += 1
            if waited % 5 == 0:
                print(f"[token_fetcher] Menunggu token... {waited}s | url: {page.url[:60]}")

        # Kalau belum dapat, reload untuk trigger lebih banyak request
        if captured["token"] is None:
            print("[token_fetcher] Belum dapat token, reload halaman...")
            try:
                page.reload(wait_until="domcontentloaded", timeout=15000)
                time.sleep(8)
            except Exception:
                pass

        context.close()

    if not captured["token"]:
        raise RuntimeError(
            "[token_fetcher] Gagal mendapatkan token.\n"
            "Pastikan:\n"
            "  1. Chrome sudah ditutup sebelum jalankan script ini\n"
            "  2. Akun stockbit.com masih login di Chrome Profile 7\n"
            "  3. Coba buka stockbit.com/stream di Chrome dulu, login, lalu tutup Chrome"
        )

    _save_token(captured["token"])
    return captured["token"]


if __name__ == "__main__":
    print("=== Stockbit Token Fetcher ===")
    token = fetch_token_via_browser(headless=False)
    print(f"\nBerhasil! Token: {token[:16]}...")
    print("Sekarang bisa jalankan: python3 scripts/collect.py BUMI")
