"""
Set Stockbit Bearer Token secara manual.

Cara ambil token:
1. Buka Chrome → stockbit.com/stream (pastikan sudah login)
2. DevTools (F12) → tab Network → refresh halaman
3. Cari request ke exodus.stockbit.com
4. Klik request → Headers → copy nilai 'Authorization: Bearer <TOKEN>'
   (jangan ikut kata 'Bearer ', copy token-nya aja)

Usage:
    python3 set_token.py
"""

import json
import time
from pathlib import Path

TOKEN_FILE = Path(__file__).parent / ".token_cache.json"


def main():
    print("=" * 55)
    print(" Stockbit Token Setup")
    print("=" * 55)
    print()
    print("Cara ambil token dari Chrome:")
    print("  1. Buka stockbit.com/stream (pastikan sudah login)")
    print("  2. DevTools (F12) → Network → refresh halaman")
    print("  3. Cari request ke exodus.stockbit.com")
    print("  4. Headers → copy nilai setelah 'Bearer '")
    print()

    token = input("Paste token di sini: ").strip()

    # Hapus prefix 'Bearer ' kalau user ikut copy
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token or len(token) < 40 or "." not in token:
        print()
        print("✗ Token tidak valid. Pastikan copy JWT yang panjang (bukan UUID pendek).")
        return

    # Cek apakah ada refresh token di cache lama
    refresh = ""
    if TOKEN_FILE.exists():
        try:
            old = json.loads(TOKEN_FILE.read_text())
            refresh = old.get("refresh_token", "")
        except Exception:
            pass

    data = {
        "access_token":  token,
        "refresh_token": refresh,
        "expires_at":    time.time() + 86400,  # 24 jam
    }

    TOKEN_FILE.write_text(json.dumps(data, indent=2))

    print()
    print(f"✓ Token tersimpan ke .token_cache.json")
    print(f"  Preview: {token[:20]}...")
    print(f"  Berlaku: 24 jam dari sekarang")
    print()
    print("Sekarang bisa jalankan: python3 cli.py")


if __name__ == "__main__":
    main()
