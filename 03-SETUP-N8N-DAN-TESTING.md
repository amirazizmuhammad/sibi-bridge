# 03 — Setup n8n, Claude API & Rencana Pengujian 🧪

> ⚠️ **Sebagian USANG.** n8n **sudah live di VPS sumopod** (workflow Active, id `qeL9Xf7C577jb9V2`) → bagian **ngrok TIDAK perlu**. AI pakai **sumopod** (`Authorization: Bearer`), bukan API key Anthropic. Rencana uji `curl` di bawah masih relevan (ganti URL ke `https://n8n-kks2xqcv5bbm.jkt5.sumopod.my.id`). Lihat juga `tools/uji-curl.md`. **Sumber kebenaran: `CLAUDE.md` + `PROGRESS.md`.**

> Anda menyebut n8n & Claude sudah siap. File ini fokus pada **menyambungkan** semuanya dan **menguji bertahap** agar mudah menemukan di mana masalahnya.

---

## A. Menyiapkan API Key Claude

1. Buka **console.anthropic.com** → **API Keys** → buat key baru → salin (mulai `sk-ant-...`).
2. Simpan baik-baik (jangan taruh di tempat publik / GitHub).
3. Isi **kredit** di akun (Billing) — tanpa kredit, API menolak permintaan.

> Estimasi biaya sangat kecil: model **Haiku 4.5** ± **$1 / 1 juta token input** dan **$5 / 1 juta token output**. Satu kalimat hanya puluhan–ratusan token. Untuk demo & pilot, beberapa dolar bisa untuk ribuan kalimat.

---

## B. Memasang Kredensial Claude di n8n

Pada node **HTTP Request** yang memanggil Claude (dibuat oleh Prompt #2), API key bisa dipasang dua cara:

- **Cara cepat:** isi langsung header `x-api-key` dengan key Anda (cukup untuk uji coba pribadi).
- **Cara rapi:** n8n → **Credentials** → buat **Header Auth** (Name: `x-api-key`, Value: key Anda), lalu pilih kredensial itu di node. Lebih aman karena key tak tertulis di workflow.

Header lain yang wajib ada di node tersebut:
```
anthropic-version: 2023-06-01
content-type: application/json
```

---

## C. Mengimpor Workflow

1. Dari Prompt #2 Anda dapat **file JSON**. Simpan sebagai `workflow-isyarat.json`.
2. n8n → pojok kanan atas **⋯ / Import** → **Import from File** → pilih file itu.
3. Buka node Claude → masukkan API key (bagian B).
4. Klik **Active** (toggle kanan atas) agar webhook hidup.
5. Catat **URL webhook** yang muncul di node Webhook (Production URL), contoh:
   `http://localhost:5678/webhook/huruf` dan `.../webhook/status`.

---

## D. Membuat Webhook Bisa Diakses dari Luar (ngrok)

Masalah: ESP32/sarung tangan (atau simulator dari HP lain) **tidak bisa** mengakses `localhost` komputer Anda. Solusinya **ngrok** — membuat alamat publik sementara ke n8n Anda.

1. Daftar & unduh ngrok dari **ngrok.com** (gratis). Login token sekali sesuai instruksinya.
2. Jalankan (port default n8n 5678):
   ```
   ngrok http 5678
   ```
3. Salin URL yang muncul, mis. `https://abc123.ngrok-free.app`.
4. URL webhook Anda jadi:
   - `https://abc123.ngrok-free.app/webhook/huruf`
   - `https://abc123.ngrok-free.app/webhook/status`
5. **Pakai URL ini** di firmware ESP32 (`N8N_URL_HURUF`) dan di dashboard (`N8N_STATUS_URL`).

> ⚠️ URL ngrok gratis **berubah** tiap kali dijalankan ulang. Setiap berubah, perbarui URL di firmware & dashboard. (Untuk pilot permanen, pertimbangkan domain/host tetap di Fase 1.)

---

## E. Rencana Pengujian Bertahap

Uji dari yang paling kecil. Kalau satu tahap gagal, perbaiki sebelum lanjut — jangan loncat.

### Tes 1 — Webhook hidup
Di PowerShell (Windows):
```powershell
curl.exe -X POST https://URL-NGROK/webhook/huruf -H "Content-Type: application/json" -d "{\"device\":\"glove-01\",\"aksi\":\"HURUF\",\"huruf\":\"A\"}"
```
**Diharapkan:** balasan JSON `{"ok":true,"buffer":"A","hasil":...}`.
**Gagal?** Cek workflow sudah **Active**, URL benar, ngrok jalan.

### Tes 2 — Buffer merangkai huruf
Kirim beberapa huruf lalu cek status:
```powershell
curl.exe -X POST https://URL-NGROK/webhook/huruf -H "Content-Type: application/json" -d "{\"aksi\":\"HURUF\",\"huruf\":\"K\"}"
curl.exe -X POST https://URL-NGROK/webhook/huruf -H "Content-Type: application/json" -d "{\"aksi\":\"HURUF\",\"huruf\":\"U\"}"
curl.exe -X GET https://URL-NGROK/webhook/status
```
**Diharapkan:** `buffer` berisi `"AKU"`.

### Tes 3 — Claude merapikan kalimat
Kirim `KIRIM`:
```powershell
curl.exe -X POST https://URL-NGROK/webhook/huruf -H "Content-Type: application/json" -d "{\"aksi\":\"KIRIM\"}"
```
**Diharapkan:** balasan memuat `hasil.teks` (mis. `"Aku."` atau hasil rapi), dan `buffer` kembali kosong.
**Gagal/`hasil` null?** Cek API key Claude, kredit akun, dan format body node Claude.

### Tes 4 — Dashboard menerima & bersuara
Buka dashboard (Prompt #3) di Chrome, set `N8N_STATUS_URL` ke `.../webhook/status`.
**Diharapkan:** subtitle berubah saat ada hasil baru; kalimat dibacakan otomatis (id-ID); tombol "Dengar" mengubah ucapan jadi teks.

### Tes 5 — Simulator penuh (tanpa hardware)
Pakai panel simulator (Prompt #4): ketik kata via tombol → KIRIM → lihat di dashboard.
**Diharapkan:** alur lengkap jalan: simulator → n8n → Claude → dashboard + suara.

### Tes 6 — Hardware penuh
Sambungkan sarung tangan (firmware Prompt #1, URL ngrok terisi).
**Diharapkan:** peragakan huruf → dashboard menampilkan & membacakan kalimat.

---

## F. Tabel Kasus Uji (untuk laporan hibah)

| # | Input | Hasil Diharapkan | Cek |
|---|---|---|---|
| 1 | huruf A | buffer = "A" | ☐ |
| 2 | A,K,U | buffer = "AKU" | ☐ |
| 3 | SPASI di tengah | buffer ada spasi | ☐ |
| 4 | HAPUS | huruf terakhir hilang | ☐ |
| 5 | "AKKU" → KIRIM | Claude → "Aku" (ejaan terkoreksi) | ☐ |
| 6 | "AKU LApAR" → KIRIM | "Aku lapar." rapi | ☐ |
| 7 | KIRIM saat buffer kosong | tidak error, hasil aman | ☐ |
| 8 | Internet putus saat KIRIM | sistem tidak crash; pesan error jelas | ☐ |
| 9 | Latensi KIRIM→hasil | catat detik (target < 3 dtk) | ☐ |
| 10 | Akurasi 1 huruf (uji 50×) | catat % benar (target awal > 80%) | ☐ |

> Simpan hasil tes #9 & #10 sebagai bukti **KPI** di laporan hibah (latensi & akurasi).

---

## G. Optimasi Biaya & Performa (penting untuk keberlanjutan)

1. **Panggil Claude sekali per kalimat**, bukan tiap huruf (sudah didesain begitu).
2. **Prompt caching** — karena `system prompt` selalu sama, aktifkan caching agar token input berulang dibayar ~10% saja (hemat s.d. 90%). Minta Claude menambahkan `cache_control` saat menulis node bila Anda mau.
3. **`max_tokens` secukupnya** (mis. 300) — output pendek = murah & cepat.
4. **Model tepat** — tetap di **Haiku 4.5** untuk tugas ringan ini; jangan pakai model termahal untuk koreksi ejaan.
5. **Batasi frekuensi polling** dashboard (1 detik cukup; jangan 100 ms).
6. **Mode offline** — bila internet putus, tampilkan `buffer` apa adanya tanpa Claude, supaya layanan tetap berjalan.

---

## H. Checklist Integrasi

- [ ] API key Claude terpasang & ada kredit
- [ ] Workflow diimpor & **Active**
- [ ] ngrok jalan, URL disalin
- [ ] Tes 1–3 (curl) lulus
- [ ] Dashboard menampilkan & membacakan (Tes 4)
- [ ] Simulator penuh lulus (Tes 5)
- [ ] Hardware penuh lulus (Tes 6)
- [ ] Catat latensi & akurasi untuk laporan

Selesai semua → Anda punya prototipe utuh untuk **demo hibah**. Lanjut ke `04-PROPOSAL-HIBAH-SMART-CITY.md` untuk menyusun proposalnya.
