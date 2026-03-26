# Stockbit Data Collector

Stockbit Data Collector adalah aplikasi CLI berbasis Python untuk mengambil (scraping) dan menyimpan data saham dari Stockbit ke dalam database MySQL lokal. Data yang diambil meliputi harga saham terkini, fundamental rasio perusahaan, metrik finansial, sejarah dividen, serta kumpulan berita terbaru tiap emiten.

## Prasyarat Lingkungan (Environment Requirements)

Sebelum mulai menjalankan aplikasi ini, silakan pastikan PC / Sistem Anda memili:

1. **Python** (versi 3.9 ke atas disarankan)
2. **MySQL Server / XAMPP** (untuk menyimpan data emiten di database lokal)
3. Komputer terhubung ke koneksi internet aktif

---

## 🛠 Panduan Setup dan Instalasi

### 1. Setup Database MySQL
1. Pastikan **MySQL Server** di dalam **XAMPP / Laragon** anda sudah berjalan (Started).
2. Buat database baru, contoh kita namai `stockbit_data`. Di phpMyAdmin atau terminal (Command Prompt/PowerShell), jalankan:
   ```sql
   CREATE DATABASE stockbit_data;
   ```
3. Import tabel-tabel aplikasi ke database yang barusan dibuat. Di dalam folder `migrations/` terdapat 4 file SQL yang harus dijalankan/di-import **secara berurutan**:
   - `migrations/schema.sql`
   - `migrations/add_columns.sql`
   - `migrations/add_news_dividend.sql`
   - `migrations/add_historical.sql`

   Anda dapat menekan tombol **Import** pada phpMyAdmin secara berurutan, atau via CLI:
   ```bash
   mysql -u root -p stockbit_data < migrations/schema.sql
   mysql -u root -p stockbit_data < migrations/add_columns.sql
   mysql -u root -p stockbit_data < migrations/add_news_dividend.sql
   mysql -u root -p stockbit_data < migrations/add_historical.sql
   ```

### 2. Setup File `.env` (Konfigurasi Database)
1. Salin (copy) file konfigurasi dari template yang ada dengan menjalankan (di Windows):
   ```bash
   copy .env.example .env
   ```
2. Buka file `.env`. Sesuaikan settingan kredensial database SQL Anda, utamanya di bagian ini:
   ```ini
   # MySQL (XAMPP)
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=stockbit_data
   DB_USER=root
   DB_PASSWORD=
   ```
   *(Kosongkan `DB_PASSWORD` jika root XAMPP/MySQL lokal Anda tidak menggunakan *password*)*

### 3. Setup Virtual Environment & Install Dependensi
Buka terminal (Command Prompt/PowerShell/VSCode Terminal) ke dalam direktori/folder proyek ini `e:\xampp\htdocs\stockbit_scrapt` dan kerjakan langkah-langkah di bawah ini:

```bash
# 1. Buat Virtual Environment bernama "venv"
python -m venv venv

# 2. Aktifkan Virtual Environment 
# [Untuk Windows (PowerShell/CMD)]
.\venv\Scripts\activate
# [Untuk Mac/Linux]
# source venv/bin/activate

# 3. Install semua package yang dibutuhkan (library python)
pip install -r requirements.txt

# 4. Install browser pendamping scraping Playwright
playwright install
```

### 4. Setup Stockbit Bearer Token
Website Stockbit memerlukan proses otentikasi. Anda harus mengatur Token sesi login agar app bisa mengambil data. Token ini disalin manual via Browser.

1. Buka browser (Chrome) lalu tuju ke laman [stockbit.com/stream](https://stockbit.com/stream). **Pastikan Anda sudah login ke akun**.
2. Buka **Developer Tools** (tekan `F12` di keyboard).
3. Pindah ke tab **Network**. Tahan biarkan tab terbuka, lalu **Refresh Halaman (F5)** web stream Stockbit Anda.
4. Di daftar aktivitas network/request yang bermunculan, carilah satu request ke arah domain `exodus.stockbit.com`.
5. Klik pinggir kiri baris request tsb, pilih kolom **Headers**, gulir bagian **Request Headers**.
6. Anda akan menemui `Authorization: Bearer <TOKEN_PANJANG_JWT>`.
7. Silakan **Copy nilai `<TOKEN_PANJANG_JWT>`** tersebut. (Cukup *token*-nya saja, tak usah bawa-bawa kata 'Bearer ').
8. Di antarmuka terminal Anda sebelumnya, ketikkan perintah:
   ```bash
   python set_token.py
   ```
9. **Paste** tokennya, lalu tekan `Enter`. Voila, applikasi akan menaruhnya di ` .token_cache.json` supaya otomatis awet sampai dengan 24 Jam penuh.

---

## 🚀 Panduan Cara Pakai (Usage Guide)

1. **Pastikan Virtual Environment berjalan**: Jika ditutup, selalu *run* lagi `.\venv\Scripts\activate` sebelum memulai.
2. Silakan hidupkan app CLI ini:
   ```bash
   python cli.py
   ```
3. Lalui antarmuka di layar. Program akan meminta **Kode Emiten** (Ticker Saham).
4. Masukkan kode tanpa perlu `.JK`. Contoh ketik yang benar:
   - `GOTO`
   - `BUMI`
   - `BBCA`
5. Aplikasi akan mengambil data (Harga Terbaru, Fundamental, Historis, hingga Berita), menampilkannnya ke layar terminal secara format yang cantik, **lalu otomatis di-save (insert/update) langsung ke database `stockbit_data`**.
6. Jika ingin keluar? Tekan Enter dan masukkan `exit` atau `q`.

---

## Ringkasan Struktur Pengerjaan Project (Folder Map)

- `cli.py` : Berisi antarmuka pengguna (tampilan utama CLI).
- `set_token.py` : Setup cache Bearer Token otentikasi dari Stream Stockbit.
- `requirements.txt` : Daftar module python agar app lancar *(library httpx, rich, mysql connector dsb)*.
- `migrations/` : Kumpulan query tabel buat MySQL (Skema App).
- `src/` : Mesin penggerak dan scraper dibalik layar, terdiri atas folder database (`repository.py`) dan kumpulan collector scrap (`fundamental.py`, `news.py`, dll).
