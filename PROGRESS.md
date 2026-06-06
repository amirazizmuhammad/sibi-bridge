# PROGRESS.md — Papan Tugas & Log Proyek SIBI-Bridge

> Claude Code: **baca file ini di awal sesi**, dan **perbarui sebelum sesi selesai** (lihat Working Agreement di `CLAUDE.md`).
> Penanda pemilik tugas: 👷 = User (hardware/manual) · 🤖 = Claude Code (software).
> Status: `[ ]` belum · `[~]` sedang dikerjakan · `[x]` selesai · `[!]` terblokir.

---

## 📍 Status Saat Ini
**Tahap:** Fase 0 — Prototipe Meja.
**Ringkas:** **Software E2E SELESAI & TERUJI LIVE.** Workflow diimpor + diaktifkan di n8n VPS sumopod (id `qeL9Xf7C577jb9V2`), tersambung ke AI sumopod (`claude-haiku-4-5`). Pipeline simulator/curl → n8n → Claude → dashboard terbukti: kalimat dirapikan (AKU→"Aku.", TLNG→"Tolong.", "Terima kasih."), HAPUS jalan, KIRIM-kosong aman, mode offline fallback, CORS OK, latensi ~1.3 dtk. Dashboard real-time diverifikasi via screenshot.
**Arah baru:** input huruf **PRIMER = kamera + MediaPipe** (`vision/`, touchless, cocok kios publik). Glove ESP32 = alternatif wearable. Backend tak berubah (input-agnostic).
**Tugas berikutnya yang disarankan:**
- 🔒 **WAJIB:** 👷 rotate kedua API key (sumopod AI + n8n) → update node Panggil Claude + isi `SIBI_TOKEN` di `sibi_common.py` + `SIBI_SECRET` di n8n Code node → **reimport workflow** (karena ada perubahan kode n8n).
- 👷 **V5:** jalankan `vision/sibi_camera.py` (mode heuristik, 10 huruf) di webcam → lihat huruf muncul di dashboard. Lalu rekam dataset + latih model untuk akurasi penuh.
- (Opsional) 👷 **H1–H6** glove bila mau varian wearable → isi `calibration/kalibrasi.md` → 🤖 perbarui kamus firmware.

---

## ✅ Fase 0 — Prototipe Meja

### Software (🤖 Claude Code)
- [x] **S1.** Workflow n8n (`n8n/workflow-isyarat.json`) — 10 node, 2 webhook (huruf/status), `workflowStaticData`, Claude hanya saat KIRIM, CORS `*`, fallback offline. JSON valid. Cara impor di `n8n/_INFO.md`.
- [x] **S2.** Alat uji — `tools/simulator.html` (tombol A–Z + SPASI/HAPUS/KIRIM, tampil balasan JSON) + `tools/uji-curl.md` (perintah PowerShell + tabel 10 kasus uji).
- [x] **S3.** Dashboard (`dashboard/index.html`) — subtitle besar, polling status 1 dtk, TTS id-ID otomatis (anti-ulang), STT "Dengar Ucapan" id-ID, mute + slider kecepatan + indikator koneksi, mode gelap kontras tinggi. Tanpa localStorage.
- [x] **S4.** Firmware ESP32 (`firmware/sibi_glove.ino`) — baca 5 sensor ADC1 + 2 tombol, deteksi huruf (jarak Euclidean < AMBANG + stabil 600 ms), tap/tahan SPASI = SPASI/HAPUS, reconnect WiFi, anti-crash POST. ⚠️ Kamus masih **PLACEHOLDER** (A/B/C) sampai `calibration/kalibrasi.md` diisi.
- [x] **S5.** Uji integrasi penuh (simulator/curl → n8n → Claude sumopod → dashboard) — **LULUS** live di VPS. Latensi ~1.3 dtk, CORS OK, fallback offline OK, dashboard real-time terverifikasi (screenshot "Terima kasih.").

### 📷 Vision — Detektor Kamera (PRIMER, 🤖 Claude Code) — folder `vision/`
- [x] **V1.** Setup Python 3.11 venv + mediapipe/opencv/sklearn + unduh `hand_landmarker.task`.
- [x] **V2.** `sibi_common.py` (config URL n8n, MediaPipe Tasks API, fitur ternormalisasi, heuristik, POST/status).
- [x] **V3.** `sibi_camera.py` (webcam → landmark → huruf → debounce → POST; keyboard SPASI/KIRIM/HAPUS; overlay; poll status). Jalur Python→n8n→Claude **LULUS** (selftest "Halo.").
- [x] **V4.** `rekam_dataset.py` + `latih_model.py` (kumpul sampel + latih KNN → `model_sibi.joblib`). Heuristik dipakai bila model belum ada.
- [x] **V6.** `dataset_dari_foto.py` — buat dataset dari **foto** (subfolder per huruf) sebagai alternatif rekam webcam. Compile OK.
- [x] **V7.** Launcher klik-dua-kali (`.bat`): `JALANKAN-KAMERA`, `REKAM-DATASET`, `LATIH-MODEL`, `FOTO-KE-DATASET` — agar user non-coder tak perlu PowerShell.
- [ ] **V5.** 👷 uji pengenalan huruf nyata (webcam atau foto) + latih model. *(Perlu kamera/foto + tangan — tak bisa diuji dari sisi 🤖.)*

### Hardware (👷 User)
- [ ] **H1.** Belanja komponen (lihat BOM di `01-PANDUAN-HARDWARE.md`).
- [ ] **H2.** Buat 5 sensor tekuk Velostat + pasang di sarung tangan.
- [ ] **H3.** Rangkai ESP32 + sensor + 2 tombol (pin: 34/35/32/33/36 + 25/26).
- [ ] **H4.** Install Arduino IDE + dukungan ESP32 + driver USB (Windows).
- [ ] **H5.** Jalankan kode tes hardware; pastikan 5 sensor & 2 tombol terbaca.
- [ ] **H6.** Kalibrasi: rekam pola tiap huruf → tulis ke `calibration/kalibrasi.md` (mulai 5–8 huruf).

### Setup/Akun (sebagian sudah via sumopod)
- [x] **A1.** AI Claude — pakai **sumopod** (`https://ai.sumopod.com/v1`, model `claude-haiku-4-5`). 🔒 key WAJIB di-rotate (bocor di chat).
- [x] **A2.** n8n sudah jalan di VPS sumopod; workflow diimpor + **Active** via API (id `qeL9Xf7C577jb9V2`).
- [~] **A3.** ngrok **TIDAK perlu** — n8n VPS sudah publik (`https://n8n-kks2xqcv5bbm.jkt5.sumopod.my.id`).
- [x] **A4.** URL n8n sudah dimasukkan ke dashboard (`N8N_STATUS_URL`) & simulator. Firmware (`N8N_URL_HURUF`) tinggal diisi URL yang sama saat pakai sarung tangan.

### Milestone Fase 0
- [ ] **M0.** Demo: peragakan beberapa huruf → kalimat muncul di layar & dibacakan. 🎉

---

## ✅ Fase 1 — Pilot Lapangan (ringkas, detail menyusul)
- [ ] Casing/enclosure rapi + speaker & layar permanen.
- [ ] Fitur STT (ucapan umum → subtitle) diuji di lapangan.
- [ ] Uji dengan pengguna nyata (Gerkatin/Pertuni); kumpulkan akurasi & kepuasan.
- [ ] Mode kalibrasi personal per pengguna.
- [ ] Dokumentasi hasil untuk laporan hibah.

## ✅ Fase 2 — Skala Smart City (ringkas)
- [ ] Banyak unit kios di lokasi publik.
- [ ] Dukungan kata/kalimat BISINDO dua tangan (2 sarung tangan + sensor gerak MPU-6050).
- [ ] Dashboard pemantauan terpusat; integrasi layanan kelurahan/RS.

---

## ⛔ Blocker / Menunggu dari User
> Daftar hal yang menghambat Claude Code. Kosongkan saat sudah tersedia.
- [!] Kamus kalibrasi (`calibration/kalibrasi.md`) masih kosong → firmware **S4 sudah ditulis** tapi pakai kamus **PLACEHOLDER** (A/B/C contoh). Belum bisa kenali huruf asli sampai 👷 selesai H6 dan kirim nilainya untuk diperbarui.
- [x] ~~URL/API key~~ → **S5 LULUS** pakai sumopod. Software tak ada blocker lagi.
- [!] 🔒 **Keamanan:** API key sumopod AI + n8n API ter-ekspos di chat → 👷 **harus regenerate** lalu pasang key baru di node Panggil Claude.
- [!] Akurasi pengenalan huruf kamera (V5) belum diuji nyata (perlu webcam + tangan user). Heuristik ~10 huruf; akurasi penuh perlu rekam dataset + latih model.

---

## 🧠 Log Keputusan (Decisions Log)
> Keputusan penting yang harus tetap konsisten lintas sesi.
| Tgl | Keputusan | Alasan |
|---|---|---|
| 2026-05-29 | Target awal = abjad jari SIBI **satu tangan** | Cocok untuk 5 sensor; BISINDO dua tangan terlalu kompleks untuk Fase 0 |
| 2026-05-29 | Sensor pakai **Velostat DIY** | Flex sensor asli terlalu mahal untuk budget |
| 2026-05-29 | Model AI = **claude-haiku-4-5** | Termurah & cepat; tugas ringan (koreksi ejaan/kalimat) |
| 2026-05-29 | AI lewat **sumopod (LiteLLM, OpenAI-compatible)** `https://ai.sumopod.com/v1/chat/completions`, bukan api.anthropic.com | User pakai n8n di VPS sumopod + model Claude dari sumopod. Node diubah: `Authorization: Bearer`, body OpenAI, parse `choices[0].message.content`. ngrok TIDAK perlu (n8n sudah publik di VPS) |
| 2026-05-29 | Workflow diimpor + diaktifkan via **n8n public API** (POST/PUT `/api/v1/workflows`), bukan UI manual | User beri API key n8n. Catatan: payload **harus UTF-8 tanpa BOM** (BOM → 500) & hanya field `name/nodes/connections/settings` |
| 2026-05-29 | **Input huruf PRIMER = kamera + MediaPipe** (folder `vision/`), glove ESP32 jadi alternatif | User tunjukkan minat skema kamera. Touchless (higienis utk kios publik), lebih akurat (21 titik), skalabel, kerja jatuh ke software. Backend input-agnostic → tak ada yang terbuang |
| 2026-05-29 | Pakai **MediaPipe Tasks API** (`HandLandmarker` + `hand_landmarker.task`), Python **3.11** venv | mediapipe 0.10.35 sudah **drop** legacy `mp.solutions.hands`; Python default 3.14 tak didukung mediapipe |
| 2026-05-29 | Prompt koreksi ditaruh di **pesan `user`** + `response_format:json_object`; parser **strip pagar ` ```json `** (ambil `{`…`}`) | Model sumopod abaikan `system` & balas obrolan/markdown-fence. Tanpa ini → selalu jatuh ke fallback (teks = buffer mentah) |
| 2026-05-29 | Perintah pakai **2 tombol fisik** (Spasi/Kirim) | Lebih andal daripada gestur perintah yang bentrok dengan huruf |
| 2026-05-29 | AI dipanggil **1× per kalimat** | Hemat biaya & cepat; tetap jalan offline untuk huruf |
| 2026-05-29 | State n8n via **workflowStaticData** | Tanpa DB eksternal; sesuai batasan stack |
| 2026-05-29 | Jarak huruf firmware pakai **Euclidean** `sqrt(Σ selisih²)`, AMBANG=25 = jarak persen | Agar nilai AMBANG di `kalibrasi.md` bermakna & mudah disetel; urutan "terdekat" tetap sama |
| 2026-05-29 | Body Claude dibangun di **Code node** lalu `jsonBody={{$json.claudeBody}}` | Hindari escaping JSON berlapis di node HTTP; `cache_control: ephemeral` dipasang utk prompt caching |
| 2026-05-29 | KIRIM saat buffer kosong → **Claude tidak dipanggil** | Hemat biaya + aman (kasus uji #7) |

---

## 📓 Log Sesi (Session Log)
> Tambahkan entri baru di ATAS tiap sesi.

### 2026-06-06 — Upload ke GitHub + proposal hibah .docx
- **Repo GitHub dibuat & di-push:** https://github.com/amirazizmuhammad/sibi-bridge (Public, 30 file, branch `main`). Semua kode + dokumentasi tersedia open-source.
- **Keamanan pra-push diverifikasi:** tidak ada API key asli dalam kode — hanya placeholder `MASUKKAN_API_KEY` / `GANTI_TOKEN_RAHASIA`. Aman dipublikasi.
- **Proposal hibah `.docx` dibuat:** `Proposal-Hibah-SIBI-Bridge.docx` (18.5 KB) — dokumen Word profesional 17 bagian, cover page, tabel RAB, metodologi Fase 0–2. (Tidak di-commit ke repo; file lokal di folder proyek.)
- **File temp dibersihkan:** `gh-auth.js`, `gh-poll.js`, `gh-create-push.js`, `gh-check.js`, `gh-auth.ps1`, `gh-auth2.ps1`, folder `docx-gen/` dihapus.
- **PAT GitHub:** `sibi-bridge-push2` (scope `repo`, exp. 6 Jul 2026) dipakai untuk push → masih aktif di settings. Token lama `sibi-bridge-push` dihapus.
- File diubah: `PROGRESS.md`.
- **Langkah berikutnya:** 👷 rotate API key sumopod + n8n → isi `SIBI_TOKEN` & `SIBI_SECRET` → reimport workflow n8n → 👷 uji V5 webcam.

### 2026-06-02 — Perbaikan semua isu medium & high dari audit mendalam
- **Audit** seluruh codebase → 13 temuan. Dikerjakan semua isu kritis + medium.
- **[HIGH] Heuristik diperluas** — tambah huruf F + komentar peta lengkap 26 huruf (mana yang perlu ML).
- **[HIGH] File CSV aman** — `rekam_dataset.py` + `dataset_dari_foto.py` kini pakai `try/finally` → data tidak hilang bila crash.
- **[HIGH] Threading HTTP** — `sibi_camera.py` kini kirim HTTP di thread terpisah via `kirim_nonblok()`. Main loop kamera tidak lagi terblokir 6 dtk bila n8n lambat.
- **[MEDIUM] HandLandmarker mode VIDEO** — `sibi_camera.py` + `rekam_dataset.py` kini pakai `RunningMode.VIDEO` + `detect_for_video(img, ts_ms)`. `buat_landmarker(mode=)` kini menerima parameter mode. `dataset_dari_foto.py` tetap IMAGE (foto statis).
- **[MEDIUM] Token keamanan endpoint n8n** — ditambahkan `SIBI_SECRET` di `n8n/workflow-isyarat.json` (node Proses Huruf), `SIBI_TOKEN` di `sibi_common.py` (env var), dan `SIBI_TOKEN` di firmware. Default = `'GANTI_TOKEN_RAHASIA'` → pemeriksaan dilewati sampai user ganti ke nilai nyata.
- **[MEDIUM] Exponential backoff polling dashboard** — `dashboard/index.html` kini pakai `jadwalkanPoll()`: sukses = reset 1 dtk, gagal = lipat dua hingga maks 30 dtk. Hemat request saat n8n mati.
- **[MEDIUM] Tombol Reset dashboard** — operator kios bisa bersihkan tampilan tanpa reload halaman.
- **[MEDIUM] Launcher dashboard** — `dashboard/BUKA-DASHBOARD.bat` (klik dua kali = buka browser).
- File diubah: `vision/sibi_common.py`, `vision/sibi_camera.py`, `vision/rekam_dataset.py`, `vision/dataset_dari_foto.py`, `n8n/workflow-isyarat.json`, `dashboard/index.html`, `firmware/sibi_glove.ino`. File baru: `dashboard/BUKA-DASHBOARD.bat`.
- **Blocker tersisa:** kalibrasi glove (H6), uji nyata V5, rotate API key, isi `SIBI_SECRET`/`SIBI_TOKEN` ke nilai nyata.
- **Langkah berikutnya:** 👷 rotate API key sumopod + n8n → isi `SIBI_TOKEN` di `sibi_common.py` & `SIBI_SECRET` di n8n → reimport workflow → 👷 uji V5 dengan webcam.

### 2026-05-29 — Audit kode akar + samakan dokumentasi (handoff)
- **Audit baris-per-baris** semua kode: vision (5 .py), firmware .ino, dashboard, simulator, workflow json.
- **Bug ditemukan & DIPERBAIKI:** `vision/sibi_common.py` heuristik huruf **A** conf `0.55` < default `--min-conf 0.6` → A tak pernah lolos di mode heuristik. Dinaikkan ke `0.60`. Diverifikasi lolos.
- Lain-lain bersih: rekam/latih/foto (header vs row 64 cocok, `q` ditangani sebelum range a-z), firmware (HTTPS via WiFiClientSecure, debounce tombol benar), dashboard/simulator (teruji live).
- **Catatan minor (bukan bug):** firmware `StaticJsonDocument` = ArduinoJson v6 (di v7 deprecated tapi tetap kompilasi); sibi_camera pakai HandLandmarker mode IMAGE (lebih berat dari VIDEO, tapi jalan).
- **Dokumentasi disamakan untuk handoff:**
  - `CLAUDE.md`: tambah blok **🟢 Status Terkini** (n8n live id, sumopod, kamera primer, key perlu rotate).
  - Banner **USANG** di `README.md`, `01`, `02`, `03` → arahkan ke CLAUDE.md + PROGRESS.md sbg sumber kebenaran; perbaiki kontrak data di `02` (anthropic→sumopod).
  - Bersihkan komentar "ngrok" di `dashboard/index.html` & `firmware/sibi_glove.ino`.
- Verifikasi akhir: 5 vision script compile OK; A lolos; workflow JSON valid (10 node). Tak ada ref `api.anthropic.com`/`x-api-key`/`ngrok` tersisa di kode.

### 2026-05-29 — Tambah jalur KAMERA (MediaPipe) sebagai input primer
- Konteks: user pilih skema **kamera** (bukan glove) → touchless, cocok kios publik. Backend n8n/Claude/dashboard dipakai apa adanya.
- Dibuat folder `vision/`:
  - venv Python **3.11** + mediapipe 0.10.35 / opencv / sklearn; unduh `hand_landmarker.task`.
  - `sibi_common.py`, `sibi_camera.py` (deteksi + kirim, keyboard kontrol, overlay, poll status), `rekam_dataset.py`, `latih_model.py`, `requirements.txt`, `_INFO.md`.
  - Pakai **MediaPipe Tasks API** (legacy `solutions.hands` sudah dihapus di 0.10.35).
- Verifikasi: 4 script compile OK; fungsi fitur/heuristik jalan (synthetic); **selftest Python→n8n→Claude LULUS** ("Halo.").
- Belum diuji: pengenalan huruf nyata (butuh webcam + tangan user) → tugas **V5**.
- Doc diperbarui: **CLAUDE.md** (tech stack, kontrak data, aturan 2/3/6, peta file), PROGRESS, `.gitignore`.
- Langkah berikutnya: 👷 jalankan `vision/sibi_camera.py` di webcam; rekam dataset + latih model untuk akurasi; rotate 2 key.

### 2026-05-29 — E2E penuh LULUS (live di sumopod)
- Dikerjakan: sambungkan + uji seluruh software ke infra sumopod user.
  - Validasi 2 key (sumopod AI + n8n API) via panggilan read-only. Model `claude-haiku-4-5` tersedia di sumopod.
  - **Impor + Activate** workflow via n8n public API → id `qeL9Xf7C577jb9V2`. (Fix: payload UTF-8 **tanpa BOM**, hanya field yg diterima.)
  - Debug Claude: model abaikan `system` + bungkus ` ```json `. Diperbaiki → prompt di pesan `user` + `response_format:json_object` + parser strip fence. **PUT update** workflow + re-activate.
  - **Uji E2E live**: AKU→"Aku.", "SAYA LAPAR"→"Saya lapar.", TLNG→"Tolong.", HAPUS (HALO→HAL), KIRIM-kosong aman, latensi ~1.3 dtk. CORS (GET `*`, preflight 204) OK.
  - Dashboard + simulator diarahkan ke URL n8n live. Dashboard diverifikasi via screenshot (subtitle real-time "Tolong." → "Terima kasih.", status "Terhubung", 0 error konsol).
- File diubah: n8n/workflow-isyarat.json (2 Code node), n8n/_INFO.md, dashboard/index.html (URL), tools/simulator.html (URL), PROGRESS.md.
- Status: **S1–S5 selesai.** Software tuntas E2E.
- Langkah berikutnya: 🔒 user rotate kedua key; 👷 hardware H1–H6 + kalibrasi → update kamus firmware → demo M0.

### 2026-05-29 — Adaptasi ke sumopod (n8n VPS + AI sumopod)
- Konteks: user sudah punya **n8n di VPS sumopod** (sudah publik → ngrok tak perlu) dan **model Claude via sumopod** (`https://ai.sumopod.com` = proxy **LiteLLM**, format **OpenAI-compatible**).
- Diubah di `n8n/workflow-isyarat.json`:
  - URL node Claude → `https://ai.sumopod.com/v1/chat/completions`.
  - Header → `Authorization: Bearer MASUKKAN_API_KEY` (hapus `x-api-key`/`anthropic-version`).
  - Body → format OpenAI (`messages:[system,user]`, `temperature`); `cache_control` dihapus. Model di `const MODEL_AI`.
  - Parse balasan → `choices[0].message.content`.
- Diperbarui `n8n/_INFO.md` (langkah key + cek model). Lolos cek JSON + sintaks JS.
- Menunggu dari user: (1) URL publik n8n, (2) nama model sumopod, (3) impor+paste key+Activate di n8n. Lalu saya uji E2E via curl dari sini.

### 2026-05-29 — Software inti S1–S4
- Dikerjakan: tulis seluruh software inti Fase 0.
  - **S1** workflow n8n (`n8n/workflow-isyarat.json`, 10 node) + cara impor di `n8n/_INFO.md`.
  - **S2** `tools/simulator.html` + `tools/uji-curl.md` (perintah PowerShell + tabel 10 kasus uji).
  - **S3** `dashboard/index.html` (subtitle besar + TTS id-ID + STT + kontrol).
  - **S4** `firmware/sibi_glove.ino` (kamus PLACEHOLDER A/B/C — `kalibrasi.md` masih kosong).
- Verifikasi: JSON workflow lolos `ConvertFrom-Json`; semua JS (2 HTML + 3 Code node) lolos cek sintaks `new Function()` via Node.
- File dibuat/diubah: n8n/workflow-isyarat.json, n8n/_INFO.md, tools/simulator.html, tools/uji-curl.md, dashboard/index.html, firmware/sibi_glove.ino, PROGRESS.md.
- Langkah berikutnya: 👷 **A1–A3** (API key, n8n Active, ngrok) → 🤖/👷 **S5** uji integrasi. 👷 **H6** kalibrasi → kirim nilai → 🤖 perbarui kamus firmware.
- Blocker baru: tidak ada (blocker lama diperbarui: S4 kini "ditulis, pakai placeholder"; S5 menunggu server).

### 2026-05-29 — Inisialisasi
- Dikerjakan: membuat dokumentasi awal (README, 01–04), `CLAUDE.md`, dan `PROGRESS.md`.
- File dibuat/diubah: README.md, 01-PANDUAN-HARDWARE.md, 02-PROMPT-UNTUK-CLAUDE.md, 03-SETUP-N8N-DAN-TESTING.md, 04-PROPOSAL-HIBAH-SMART-CITY.md, CLAUDE.md, PROGRESS.md.
- Langkah berikutnya: 🤖 mulai Tugas **S1** (workflow n8n) + 🤖 **S2** (simulator) agar bisa uji tanpa hardware; 👷 mulai **H1** (belanja) & **A1** (API key).
- Blocker baru: (lihat bagian Blocker).
