# Uji Pipeline n8n via curl (PowerShell) — Tugas S2

> Alat uji **tanpa hardware**. Pasangan dari `tools/simulator.html` (versi tombol-klik).
> Gunakan untuk memverifikasi endpoint `POST /webhook/huruf` dan `GET /webhook/status`.

## Persiapan
1. Workflow n8n sudah **Active** (lihat `n8n/_INFO.md`).
2. Ganti `URL` di bawah dengan URL Anda:
   - Lokal: `http://localhost:5678`
   - Publik (HP/ESP32): URL ngrok, mis. `https://abc123.ngrok-free.app`
3. Buka **PowerShell** (Windows). Pakai `curl.exe` (bukan alias `curl` PowerShell) agar argumen `-d`/`-H` benar.

Set variabel sekali agar perintah pendek:
```powershell
$URL = "http://localhost:5678"
```

---

## Skenario lengkap: mengeja "AKU LAPAR" lalu KIRIM

### 1) Kirim huruf satu per satu: A, K, U
```powershell
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"device\":\"glove-01\",\"aksi\":\"HURUF\",\"huruf\":\"A\"}'
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"device\":\"glove-01\",\"aksi\":\"HURUF\",\"huruf\":\"K\"}'
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"device\":\"glove-01\",\"aksi\":\"HURUF\",\"huruf\":\"U\"}'
```
**Diharapkan** (balasan terakhir):
```json
{"ok":true,"buffer":"AKU","hasil":null}
```

### 2) Spasi
```powershell
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"SPASI\"}'
```
**Diharapkan:** `{"ok":true,"buffer":"AKU ","hasil":null}`

### 3) Lanjut: L, A, P, A, R
```powershell
"L","A","P","A","R" | ForEach-Object {
  curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d ('{\"aksi\":\"HURUF\",\"huruf\":\"' + $_ + '\"}')
  ""  # baris kosong biar enak dibaca
}
```
**Diharapkan** (balasan terakhir): `{"ok":true,"buffer":"AKU LAPAR","hasil":null}`

### 4) Cek buffer via status (sebelum KIRIM)
```powershell
curl.exe -s "$URL/webhook/status"
```
**Diharapkan:**
```json
{"buffer":"AKU LAPAR","hasil":null,"ts":1730000000000}
```

### 5) KIRIM → Claude merapikan kalimat
```powershell
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"KIRIM\"}'
```
**Diharapkan** (buffer dikosongkan, `hasil` terisi dari Claude):
```json
{"ok":true,"buffer":"","hasil":{"teks":"Aku lapar.","untuk_suara":"Aku lapar"},"ts":1730000000000}
```

### 6) Cek status lagi (untuk dashboard)
```powershell
curl.exe -s "$URL/webhook/status"
```
**Diharapkan:** `{"buffer":"","hasil":{"teks":"Aku lapar.","untuk_suara":"Aku lapar"},"ts":...}`

---

## Uji HAPUS (hapus huruf terakhir)
```powershell
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"HURUF\",\"huruf\":\"A\"}'
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"HURUF\",\"huruf\":\"B\"}'
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"HAPUS\"}'
```
**Diharapkan:** buffer berakhir `"...A"` (huruf `B` terhapus).

---

## Tabel Kasus Uji

| # | Input | Hasil yang Diharapkan | Catatan |
|---|-------|----------------------|---------|
| 1 | `HURUF A` | `buffer:"A"`, `hasil:null` | huruf masuk buffer |
| 2 | A, K, U | `buffer:"AKU"` | rangkai huruf |
| 3 | SPASI di tengah | `buffer:"AKU "` | spasi masuk |
| 4 | A, B, HAPUS | `buffer:"A"` | huruf terakhir hilang |
| 5 | `AKKU` → KIRIM | `hasil.teks:"Aku"` | Claude koreksi ejaan ganda |
| 6 | `AKU LApAR` → KIRIM | `hasil.teks:"Aku lapar."` | Claude rapikan kapital + titik |
| 7 | KIRIM saat buffer kosong | tidak error; `hasil` = nilai terakhir/`null`; Claude **tidak** dipanggil | hemat biaya + aman |
| 8 | KIRIM saat internet putus | tidak crash; `hasil.teks` = buffer apa adanya (mode offline) | fallback di node Simpan Hasil |
| 9 | KIRIM → ukur waktu balas | catat detik (target < 3 dtk) | KPI latensi laporan hibah |
| 10 | 1 huruf diulang 50× (nanti via hardware) | catat % benar (target awal > 80%) | KPI akurasi |

### Cara uji kasus 5 (salah eja "AKKU")
```powershell
"A","K","K","U" | ForEach-Object {
  curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d ('{\"aksi\":\"HURUF\",\"huruf\":\"' + $_ + '\"}'); ""
}
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"KIRIM\"}'
```
**Diharapkan:** `hasil.teks` ≈ `"Aku"` (Claude menebak kata wajar). Nilai persis bisa beda — yang penting masuk akal Bahasa Indonesia.

### Cara uji kasus 7 (KIRIM buffer kosong)
```powershell
curl.exe -s -X POST "$URL/webhook/huruf" -H "Content-Type: application/json" -d '{\"aksi\":\"KIRIM\"}'
```
**Diharapkan:** balasan aman (`hasil` = nilai sebelumnya atau `null`), Claude tidak dipanggil (cek di Executions n8n: tidak ada panggilan HTTP).

---

## Kalau gagal
- **`Failed to connect` / timeout** → n8n belum jalan / URL salah / belum `ngrok`.
- **HTTP 404** → workflow belum **Active**, atau path salah (harus `huruf` / `status`).
- **`hasil` selalu `null` setelah KIRIM** → cek API key Claude di node **Panggil Claude**, kredit akun, dan format body. Lihat tab **Executions** di n8n untuk pesan error node.
- **Error CORS** (hanya di browser/simulator, bukan curl) → pastikan opsi `allowedOrigins:*` ada di node Webhook (sudah disetel di workflow ini).

> Tip: tab **Executions** di n8n memperlihatkan jalur tiap permintaan node-per-node — alat debug terbaik.
