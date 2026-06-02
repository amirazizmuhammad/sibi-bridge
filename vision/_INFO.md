# Folder: vision/ — 📷 Detektor Huruf SIBI via Kamera (PRIMER Fase 0)

Webcam → MediaPipe (21 titik tangan) → huruf → POST ke webhook n8n yang **sama**.
Backend (n8n + Claude + dashboard) **tidak berubah** — kamera hanya pengganti sumber huruf (dulu sarung tangan).

> Status: terpasang & teruji jalur Python→n8n (selftest LULUS). Pengenalan huruf nyata perlu **webcam + tanganmu** untuk diuji.

## Isi
| File | Guna |
|------|------|
| `sibi_camera.py` | Aplikasi utama: kamera → deteksi huruf → kirim ke n8n |
| `rekam_dataset.py` | Rekam contoh tiap huruf (untuk model akurat) → `dataset.csv` |
| `latih_model.py` | Latih classifier dari `dataset.csv` → `model_sibi.joblib` |
| `sibi_common.py` | Pustaka bersama (konfigurasi URL n8n, MediaPipe, fitur, heuristik) |
| `hand_landmarker.task` | Model tangan MediaPipe (sudah terunduh, 7.6 MB) |
| `.venv/` | Lingkungan Python 3.11 + paket (sudah terpasang) |

## Cara pakai (Windows PowerShell)

> Sudah saya siapkan venv + paket. Langsung jalankan dari folder `vision/`.

### 1) Uji cepat tanpa kamera (membuktikan tersambung ke n8n)
```powershell
.\.venv\Scripts\python.exe sibi_camera.py --selftest
```
Harus muncul `hasil.teks = Halo.` → jalur Python → n8n → Claude OK. ✅

### 2) Jalankan kamera (mode HEURISTIK — langsung bisa, ~10 huruf jelas)
```powershell
.\.venv\Scripts\python.exe sibi_camera.py
```
Jendela kamera terbuka. Peragakan huruf; saat stabil ~0,8 dtk → terkirim ke n8n → muncul di dashboard + dibacakan.
- Kalau kamera salah, coba `--camera 1`.
- Uji deteksi tanpa kirim: tambah `--no-send`.

**Kontrol keyboard (klik dulu jendela kamera):**
`SPASI`=spasi · `ENTER`=KIRIM (panggil Claude) · `BACKSPACE`=HAPUS · `A`=auto-kirim ON/OFF · `S`=kirim huruf manual · `Q`/`ESC`=keluar.

### 3) Mode AKURAT (latih model — disarankan untuk demo serius)
Heuristik terbatas. Untuk semua huruf + akurasi tinggi:
```powershell
# a. Rekam contoh: tekan tombol huruf (A-Z) sambil peragakan, tahan ~2 dtk. Ulangi tiap huruf 2-3x.
.\.venv\Scripts\python.exe rekam_dataset.py
#    Target >= 50-100 contoh/huruf. Mulai 5-8 huruf jelas dulu (A,B,C,I,L,O,U,Y). Q = simpan.

# b. Latih:
.\.venv\Scripts\python.exe latih_model.py
#    Menyimpan model_sibi.joblib + lapor akurasi.

# c. Jalankan lagi — otomatis pakai model:
.\.venv\Scripts\python.exe sibi_camera.py
```

## Tips akurasi
- Cahaya cukup, tangan penuh di frame, latar tak ramai.
- Rekam dataset dari beberapa sudut/jarak/tangan agar model kuat.
- Huruf gerak (J, Z) belum didukung (statis dulu) — sama seperti batasan Fase 0.

## Catatan
- **Tanpa API key di Python** — kamera hanya POST ke webhook n8n publik. Aman.
- **Privasi:** hanya angka landmark yang diproses; **tidak** menyimpan gambar/video. `dataset.csv` berisi angka saja.
- Ganti server n8n: set env `N8N_BASE`, atau ubah `N8N_BASE` di `sibi_common.py`.
- Memasang ulang di komputer lain:
  ```powershell
  py -3.11 -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
  curl.exe -L -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
  ```
