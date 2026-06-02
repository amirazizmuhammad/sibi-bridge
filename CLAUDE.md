# CLAUDE.md — Konteks Proyek untuk Claude Code

> File ini dibaca otomatis oleh Claude Code di awal **setiap** sesi. Dibuat ringkas (sengaja < 150 baris) agar selalu dipatuhi. Detail panjang ada di file dokumentasi lain.

## Tentang Proyek
**SIBI-Bridge**: alat layanan publik yang menerjemahkan abjad jari (SIBI) → teks → suara, dan ucapan → teks. Satu alat melayani **tuna rungu, tuna wicara, tuna netra**. Untuk hibah & Smart City.

## 🟢 Status Terkini (handoff — baca ini + PROGRESS.md dulu)
- **Backend LIVE & teruji**: n8n di VPS sumopod, workflow id `qeL9Xf7C577jb9V2`, **Active**. Webhook: `https://n8n-kks2xqcv5bbm.jkt5.sumopod.my.id/webhook/{huruf,status}`.
- **AI**: sumopod `claude-haiku-4-5` (OpenAI-compatible). Key tertanam di node "Panggil Claude".
- **Input PRIMER = kamera** (`vision/`, Python 3.11 venv siap). Backend input-agnostic. Glove ESP32 = alternatif (kamus PLACEHOLDER, belum dikalibrasi).
- **Selesai**: S1–S5 (backend+dashboard+simulator E2E LULUS), V1–V7 (modul kamera). **Belum**: V5 = uji pengenalan huruf nyata (perlu webcam+tangan user); kalibrasi glove.
- ⚠️ **Doc lama 01–04 + README sebagian USANG** (tulis endpoint anthropic/x-api-key, glove-primer, ngrok). **Sumber kebenaran = CLAUDE.md + PROGRESS.md.** Realita: sumopod (bukan anthropic), kamera primer, n8n di VPS (tanpa ngrok).
- 🔒 API key (sumopod + n8n) pernah ter-ekspos di chat → user diminta rotate.

## Pembagian Peran (PENTING)
- **User = HARDWARE saja**: merakit, menyolder, mengkalibrasi, menyambung ESP32.
- **Claude Code = SEMUA SOFTWARE**: menulis firmware ESP32, workflow n8n, dashboard web, alat uji, dan **menjaga dokumentasi tetap terbarui**.
- Jangan minta user menulis kode. Berikan file jadi + instruksi pasang yang sederhana.

## Tech Stack
- **Input huruf (PRIMER Fase 0):** 📷 **Kamera + MediaPipe Tasks (Python 3.11, `vision/`)** — touchless, cocok kios publik. 🧤 Alternatif "wearable": ESP32 + 5 sensor tekuk + 2 tombol (`firmware/`).
- Orkestrasi: **n8n** (low-code, jalan di VPS sumopod).
- AI: model **`claude-haiku-4-5`** via **sumopod** (proxy LiteLLM, OpenAI-compatible). Endpoint `https://ai.sumopod.com/v1/chat/completions`, header `Authorization: Bearer <key>`, balasan dari `choices[0].message.content`. (BUKAN api.anthropic.com.)
- Output: 1 file HTML di browser (subtitle + Text-to-Speech `id-ID` + Speech-to-Text). Tanpa backend/DB lain.

## Kontrak Data (WAJIB konsisten di firmware, n8n, dashboard)
- Detektor (kamera `camera-01` ATAU glove `glove-01`) → `POST /webhook/huruf` body: `{"device":"camera-01","aksi":"HURUF","huruf":"A"}`
  - `aksi` ∈ `HURUF` | `SPASI` | `KIRIM` | `HAPUS`. (Mode kamera: SPASI/KIRIM/HAPUS via keyboard.)
  - Backend n8n **input-agnostic**: sumber apa pun yang patuh kontrak ini diterima — tak perlu ubah n8n/dashboard.
- Dashboard → `GET /webhook/status` balasan: `{"buffer":"AKU LAPAR","hasil":{"teks":"Aku lapar.","untuk_suara":"Aku lapar"},"ts":123}`
- n8n simpan state pakai `workflowStaticData` (TANPA database eksternal). Claude dipanggil **hanya saat `KIRIM`**, bukan tiap huruf.

## Konvensi & Aturan Teknis (jangan dilanggar)
1. Sensor analog ESP32 **hanya pin ADC1**: thumb=34, index=35, middle=32, ring=33, pinky=36. Tombol digital: SPASI=25, KIRIM=26 (`INPUT_PULLUP`). (ADC2 mati saat WiFi.)
2. Deteksi huruf di **sisi detektor** (kamera: MediaPipe 21-titik → classifier ML/heuristik; glove: ESP32 cocokkan kamus kalibrasi). Pakai debounce (huruf stabil ~600–800 ms). Kirim HURUF jadi, bukan data mentah.
3. AI dipanggil **1× per kalimat** (hanya saat `KIRIM`). `max_tokens` ~200 + `response_format:json_object`; instruksi di pesan `user` (model sumopod abaikan `system`); parser buang pagar kode di balasan + fallback offline.
4. **Mode offline**: jika internet putus, tampilkan `buffer` apa adanya tanpa AI; jangan crash.
5. Dashboard: **JANGAN** pakai localStorage/sessionStorage. CORS `Access-Control-Allow-Origin: *` di webhook.
6. Privasi: jangan simpan rekaman suara/biometrik. Kamera: proses **angka landmark** saja, JANGAN simpan gambar/video. `buffer` dikosongkan tiap kalimat selesai.
7. Komentar kode & teks UI dalam **Bahasa Indonesia**.
8. Target awal = **abjad jari SIBI satu tangan**. BISINDO dua tangan = Fase 2, jangan diklaim selesai di Fase 0.
9. **Jangan menimpa** isi `calibration/kalibrasi.md` (nilai sensor hasil rekam user) tanpa diminta. Itu data fisik milik user.

## Peta File / Struktur Folder
```
sibi-bridge/
├── CLAUDE.md                       ← file ini (auto-dibaca)
├── PROGRESS.md                     ← papan tugas & log (BACA & UPDATE tiap sesi)
├── README.md                       ← gambaran besar
├── 01-PANDUAN-HARDWARE.md          ← panduan rakit (untuk user)
├── 02-PROMPT-UNTUK-CLAUDE.md       ← spesifikasi tugas tiap komponen software
├── 03-SETUP-N8N-DAN-TESTING.md     ← setup n8n + rencana uji
├── 04-PROPOSAL-HIBAH-SMART-CITY.md ← kerangka proposal hibah
├── vision/                         ← 📷 detektor kamera (PRIMER): sibi_camera.py, rekam_dataset.py, latih_model.py, sibi_common.py
├── firmware/sibi_glove.ino         ← 🧤 alternatif glove (ESP32)
├── n8n/workflow-isyarat.json       ← workflow (sudah live di VPS sumopod)
├── dashboard/index.html            ← subtitle + TTS + STT
├── tools/simulator.html            ← simulator + uji-curl.md
└── calibration/kalibrasi.md        ← nilai sensor per huruf (diisi user, untuk glove)
```
Saat membuat software, ikuti **spesifikasi di `02-PROMPT-UNTUK-CLAUDE.md`** dan kontrak data di atas.

## ✅ Working Agreement (cara kerja tiap sesi)
1. **Di awal sesi:** baca `PROGRESS.md` untuk tahu status terakhir, blocker, dan tugas berikutnya. Konfirmasi singkat ke user apa yang akan dikerjakan.
2. **Selama bekerja:** kerjakan 1 tugas hingga tuntas & teruji sebisanya.
3. **Sebelum sesi selesai (WAJIB):** perbarui `PROGRESS.md`:
   - centang tugas yang selesai, tandai yang sedang berjalan;
   - perbarui bagian **Status Saat Ini**;
   - tambahkan 1 entri di **Log Sesi** (tanggal, yang dikerjakan, file diubah, langkah berikutnya, blocker baru).
4. Jika sebuah keputusan teknis berubah, catat di **Log Keputusan** di `PROGRESS.md` dan, bila perlu, perbarui file dokumentasi terkait agar tidak ada info usang.
5. Jika user lupa, **ingatkan**: "Mau saya update PROGRESS.md sebelum kita berhenti?"

> Catatan: Claude Code juga punya "auto memory", tapi papan tugas terstruktur ini sengaja disimpan sebagai file agar bisa dibaca manusia, di-commit ke git, dan tahan walau ganti perangkat/sesi.
