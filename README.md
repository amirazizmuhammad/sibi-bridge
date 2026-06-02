# 🤟 SIBI-Bridge — Jembatan Komunikasi Disabilitas berbasis IoT + Claude AI + n8n

> ⚠️ **STATUS TERKINI — sebagian dokumen di bawah USANG (rencana awal).**
> Realita sekarang:
> - **Input PRIMER = kamera + MediaPipe** (folder `vision/`, touchless) — sarung tangan ESP32 jadi **alternatif**.
> - **AI via sumopod** (`https://ai.sumopod.com`, OpenAI-compatible), **BUKAN** api.anthropic.com.
> - **n8n LIVE di VPS sumopod** (tanpa ngrok), workflow Active. Backend + dashboard sudah **teruji E2E**.
> **Sumber kebenaran = `CLAUDE.md` + `PROGRESS.md`.** Teks "sarung tangan / Anthropic / ngrok" di bawah = konteks rencana awal.

> Sistem penerjemah bahasa isyarat → teks → suara, sekaligus suara → teks, yang menghubungkan **tuna rungu, tuna wicara, dan tuna netra** dalam satu alat. Dirancang untuk kios layanan publik (Smart City) dan pemanfaatan masyarakat luas.

---

## 1. Apa yang Sedang Kita Bangun

Bayangkan sebuah **kios kecil** di kelurahan, rumah sakit, atau halte. Di situ ada 1 sarung tangan sensor + 1 tablet/layar + speaker. Alat ini menjadi **penerjemah dua arah**:

```
┌─────────────────────────────────────────────────────────────┐
│                    SIBI-BRIDGE (1 alat, 3 manfaat)            │
├─────────────────────────────────────────────────────────────┤
│  TUNA WICARA  → memperagakan isyarat di sarung tangan         │
│                 → keluar TEKS di layar + SUARA dari speaker   │
│                                                               │
│  TUNA RUNGU   → melihat TEKS/subtitle di layar                │
│                 (ucapan lawan bicara → teks otomatis)         │
│                                                               │
│  TUNA NETRA   → mendengar SUARA dari speaker                  │
│                 (semua yang diperagakan/ditulis → dibacakan)  │
└─────────────────────────────────────────────────────────────┘
```

Inti idenya: **satu pesan, tiga bentuk** (gerak → teks → suara). Itulah kenapa ketiga kelompok bisa dilayani satu alat. Inilah "kebaruan" yang kuat untuk proposal hibah Anda — bukan sekadar penerjemah isyarat, tapi **jembatan komunikasi inklusif**.

---

## 2. Tech Stack (sesuai batasan Anda)

| Lapisan | Teknologi | Peran |
|---|---|---|
| **IoT / Hardware** | ESP32 + sensor jari + 2 tombol | Membaca gerakan tangan, kirim data |
| **Orkestrasi** | n8n | Menerima data, atur alur, panggil AI, simpan hasil |
| **Kecerdasan** | Claude API (model **Haiku 4.5**) | Perbaiki ejaan, susun kalimat alami, siapkan teks untuk suara |
| **Output** | Halaman web (dibuat Claude) | Tampilkan subtitle + bicara (Text-to-Speech) + dengar ucapan (Speech-to-Text) |

> **Tidak perlu** database, server backend, atau bahasa pemrograman lain. Output cukup halaman web yang dibuka di tablet/HP/PC. Semua tetap di dalam stack: **IoT + n8n + Claude**.

---

## 3. Arsitektur Sistem

```
 [Sarung Tangan ESP32]
   5 sensor jari + 2 tombol (Spasi / Kirim)
        │
        │  ESP32 mendeteksi HURUF secara lokal (cepat, gratis, offline)
        │  lalu kirim huruf via WiFi (HTTP POST)
        ▼
 ┌──────────────────────────────┐
 │            n8n               │
 │  POST /webhook/huruf         │  ← terima tiap huruf, susun jadi kata/kalimat
 │  → saat tombol KIRIM ditekan:│
 │     panggil Claude Haiku 4.5 │  ← rapikan ejaan + jadikan kalimat alami
 │  GET  /webhook/status        │  ← layar mengambil hasil terbaru (polling)
 └──────────────────────────────┘
        │                         ▲
        ▼ (hasil teks rapi)       │ (polling tiap 1 detik)
 ┌──────────────────────────────┐
 │   Halaman Web (Dashboard)    │
 │   • Subtitle besar di layar  │  → untuk TUNA RUNGU
 │   • Suara otomatis (TTS-ID)  │  → untuk TUNA NETRA & umum
 │   • Tombol "Dengar" (STT)    │  → ucapan umum jadi teks utk TUNA RUNGU
 └──────────────────────────────┘
```

**Kenapa deteksi huruf dilakukan di ESP32, bukan di Claude?** Supaya cepat, gratis, dan tetap jalan walau internet lemah. Claude hanya dipanggil **sekali per kalimat** (saat tombol Kirim) untuk merapikan ejaan & menyusun kalimat — bukan tiap gerakan jari. Ini membuat sistem **murah & cepat** (penting untuk keberlanjutan hibah).

---

## 4. Pembagian Peran: Anda vs Claude

Permintaan Anda: *Anda fokus hardware, Claude urus semua software.* Inilah pembagiannya:

| 👷 ANDA (Hardware) | 🤖 CLAUDE (Software) |
|---|---|
| Beli & rakit komponen | Tulis firmware ESP32 (kode Arduino) |
| Solder sensor + tombol ke sarung tangan | Buat workflow n8n (file siap-impor) |
| Pasang ESP32, colok USB | Buat halaman web dashboard (subtitle + suara) |
| Jalankan tes sensor sederhana | Buat skrip kalibrasi & pengujian |
| Kalibrasi (rekam pola tiap huruf) | Perbaiki bug bila ada error |

Caranya: **salin-tempel prompt** dari file `02-PROMPT-UNTUK-CLAUDE.md` ke Claude, lalu Claude memberi Anda kode/file jadi. Anda tinggal pasang.

---

## 5. Isi Paket Dokumen Ini

| File | Untuk Apa | Dibaca Oleh |
|---|---|---|
| **README.md** | Gambaran besar (file ini) | Anda |
| **01-PANDUAN-HARDWARE.md** | Belanja, rakit, solder, kalibrasi, atasi error | Anda (fokus utama) |
| **02-PROMPT-UNTUK-CLAUDE.md** | Prompt siap-tempel agar Claude buatkan semua software | Anda → tempel ke Claude |
| **03-SETUP-N8N-DAN-TESTING.md** | Pasang n8n, impor workflow, set API, rencana uji | Anda |
| **04-PROPOSAL-HIBAH-SMART-CITY.md** | Kerangka proposal, RAB, timeline, KPI, etika data, mitra | Anda (untuk hibah) |
| **CLAUDE.md** | Konteks proyek yang dibaca Claude Code otomatis tiap sesi | 🤖 Claude Code (auto) |
| **PROGRESS.md** | Papan tugas hidup + log; dibaca & diupdate Claude Code tiap sesi | 🤖 + Anda |

---

## 6. Roadmap 3 Fase

### Fase 0 — Prototipe Meja (Minggu 1–4) 🎯 *MULAI DI SINI*
- 1 sarung tangan, 5 sensor jari, 2 tombol, ESP32.
- Target: kenali **abjad jari (A–Z)** satu tangan, rangkai jadi kata → kalimat lewat Claude → tampil & bersuara.
- Output: halaman web di laptop Anda.

### Fase 1 — Pilot Lapangan (Bulan 2–4)
- Casing rapi, layar + speaker permanen, uji dengan pengguna nyata (komunitas tuli/Gerkatin).
- Tambah fitur Speech-to-Text (ucapan umum → subtitle untuk tuna rungu).
- Kumpulkan data akurasi & umpan balik (bahan laporan hibah).

### Fase 2 — Skala Smart City (Bulan 5–12)
- Banyak unit kios di lokasi publik.
- Tambah kalimat/kata BISINDO dua tangan (perlu 2 sarung tangan + sensor gerak).
- Dashboard pemantauan terpusat, integrasi layanan kelurahan/RS.

---

## 7. ⚠️ Keputusan Teknis Penting (Baca Sebelum Belanja!)

Saya perlu jujur soal beberapa hal supaya proyek Anda realistis dan proposal hibah Anda kredibel:

### a. Target awal = ABJAD JARI (fingerspelling), bukan kalimat BISINDO penuh
- **SIBI** dan **abjad jari** sebagian besar **satu tangan** dan posisinya relatif statis → **cocok** untuk sarung tangan 5 sensor.
- **BISINDO** (bahasa isyarat alami komunitas Tuli) banyak memakai **dua tangan + gerakan + ekspresi wajah** → butuh 2 sarung tangan, sensor gerak (MPU-6050), dan model urutan-waktu. Ini **Fase 2**, jangan dijanjikan di prototipe awal.
- **Saran:** di proposal, posisikan Fase 0–1 sebagai "pengenalan abjad jari + perangkaian kata/kalimat oleh AI", dan BISINDO penuh sebagai roadmap. Ini lebih jujur dan tetap menarik.

### b. Sensor flex asli itu MAHAL di Indonesia
- Flex sensor asli (Spectra Symbol) ~Rp 80.000–150.000 **per buah**. 5 buah bisa menghabiskan seluruh budget.
- **Solusi hemat:** buat sensor tekuk sendiri dari **Velostat** (lembaran konduktif peka-tekanan) ~Rp 60.000 untuk **banyak** sensor. Detail cara buat ada di `01-PANDUAN-HARDWARE.md`.

### c. Pin analog ESP32 ada jebakan
- Saat WiFi menyala, pin **ADC2 tidak berfungsi**. Wajib pakai pin **ADC1**: GPIO **32, 33, 34, 35, 36**. (Detail di panduan hardware — ini sumber error paling sering.)

### d. Biaya Claude API itu kecil — kalau dirancang benar
- Pakai model **Claude Haiku 4.5** (paling murah & cepat): sekitar **$1 per 1 juta token input, $5 per 1 juta token output**. Satu kalimat hanya butuh ratusan token → **sangat murah** karena Claude dipanggil sekali per kalimat, bukan tiap gerakan.
- Aktifkan **prompt caching** (hemat s.d. 90% token input berulang). Ini menjadi argumen "biaya operasional rendah" yang kuat di proposal hibah.

---

## 8. 💡 Apa Lagi yang Dibutuhkan? (Saran Saya)

Anda bertanya "kira-kira apa lagi yang dibutuhkan". Berikut yang sering terlupa tapi penting — terutama untuk hibah & manfaat publik:

### Teknis & Produk
1. **Tombol kontrol fisik (2 buah)** — untuk "Spasi" dan "Kirim". Jauh lebih andal daripada menebak-nebak gestur perintah. Murah (~Rp 2.000/buah).
2. **Casing / wadah** — agar alat tahan dipakai publik (3D print atau kotak plastik). Penting untuk pilot lapangan.
3. **Power bank / baterai** — agar kios tidak harus selalu colok listrik.
4. **Mode offline darurat** — ESP32 tetap kenali huruf walau internet putus; hasil ditampilkan tanpa "pemolesan" Claude.
5. **OLED kecil di sarung tangan (opsional)** — tampilkan huruf yang sedang dibentuk, membantu pengguna mengoreksi.

### Untuk Hibah & Masyarakat
6. **Validasi dengan komunitas Tuli/Tuna netra sejak awal** — libatkan **Gerkatin** (komunitas tuli) & **Pertuni** (tuna netra). Penilai hibah sangat menghargai keterlibatan pengguna asli. Ini juga mencegah desain yang keliru.
7. **Persetujuan & privasi data (UU PDP No. 27/2022)** — suara & gerakan adalah data pribadi. Siapkan kebijakan privasi & informed consent. (Kerangka ada di proposal.)
8. **Indikator keberhasilan terukur (KPI)** — akurasi pengenalan huruf (%), waktu respons (detik), jumlah pengguna, skor kepuasan. Wajib ada di laporan hibah.
9. **Rencana keberlanjutan** — biaya per unit, perawatan, model open-source agar bisa direplikasi pemda lain.
10. **Dokumentasi & video demo** — untuk presentasi hibah dan diseminasi.

### Legal/Administratif Hibah
11. **Mitra resmi** — surat dukungan dari Dinas Sosial / Diskominfo / kampus / komunitas disabilitas.
12. **Hak kekayaan intelektual** — pertimbangkan pencatatan ciptaan/hak cipta untuk perangkat lunak & desain.

---

## 9. Langkah Berikutnya yang Saya Sarankan

1. **Baca** `01-PANDUAN-HARDWARE.md` → tentukan: Velostat (hemat) atau flex sensor asli.
2. **Belanja** komponen sesuai BOM.
3. Sambil menunggu komponen datang, **tempel prompt #1 & #2** dari `02-PROMPT-UNTUK-CLAUDE.md` ke Claude → dapatkan firmware & workflow n8n.
4. **Impor workflow** ke n8n (panduan di file 03), set API key Claude, uji webhook pakai `curl`.
5. Komponen datang → **rakit & kalibrasi** → sambungkan ke n8n → demo pertama!

---

*Dokumen ini disusun sebagai fondasi proyek. Semua angka harga & statistik bersifat estimasi/ilustrasi — verifikasi harga terbaru di toko komponen, dan data disabilitas dari sumber resmi (BPS, Kemensos, Satu Data Indonesia) untuk proposal final.*
