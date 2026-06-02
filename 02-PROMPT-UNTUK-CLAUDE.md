# 02 — Prompt Siap-Pakai untuk Claude 🤖

> ⚠️ **Sebagian USANG.** Kontrak data inti (aksi `HURUF/SPASI/KIRIM/HAPUS`, `/webhook/huruf`, `/webhook/status`) **masih berlaku**. TAPI semua software **sudah dibuat & live** (`n8n/`, `dashboard/`, `tools/`, `vision/`, `firmware/`) — prompt di bawah hanya arsip. Perubahan penting: **AI = sumopod** (OpenAI-compatible), bukan Anthropic; **input primer = kamera** (`vision/`). **Sumber kebenaran: `CLAUDE.md` + `PROGRESS.md`.**

> Cara pakai: **salin** isi tiap blok prompt (yang di dalam kotak), **tempel ke Claude** (chat baru atau lanjutan), kirim. Claude akan memberi Anda kode/file jadi. Anda tinggal pasang. Kerjakan **berurutan** dari Prompt #1.

> Catatan: tiap prompt sengaja "lengkap sendiri" (memuat semua konteks) supaya bisa ditempel ke Claude mana pun tanpa harus menjelaskan ulang proyek.

---

## 📋 KONTRAK DATA (acuan semua komponen)

Agar firmware, n8n, dan dashboard "berbicara" sama, semuanya mengikuti aturan ini. Anda tidak perlu menghafal — sudah tertanam di tiap prompt.

**Endpoint n8n:**
- `POST /webhook/huruf` — ESP32 mengirim tiap kejadian. Body:
  ```json
  { "device": "glove-01", "aksi": "HURUF", "huruf": "A" }
  ```
  Nilai `aksi`: `"HURUF"` (kirim 1 huruf), `"SPASI"` (tombol spasi), `"KIRIM"` (tombol kirim → minta Claude rapikan), `"HAPUS"` (hapus 1 huruf terakhir).
- `GET /webhook/status` — dashboard polling tiap 1 dtk. Balasan:
  ```json
  { "buffer": "AKU LAPAR", "hasil": { "teks": "Aku lapar.", "untuk_suara": "Aku lapar" }, "ts": 123 }
  ```

**Model AI (TERKINI):** `claude-haiku-4-5` via **sumopod** — endpoint `https://ai.sumopod.com/v1/chat/completions`, header `Authorization: Bearer <key>`, body format **OpenAI** (`messages`, `response_format:json_object`), balasan dibaca dari `choices[0].message.content`. *(Endpoint Anthropic `api.anthropic.com` di blok prompt bawah = USANG, jangan dipakai.)*

---

## ✅ PROMPT #1 — Firmware ESP32 (deteksi huruf + kirim ke n8n)

**Tujuan:** dapat satu file `.ino` yang membaca sensor, mengenali huruf dari kamus kalibrasi, dan mengirim ke n8n.

> ⚠️ Sebelum menempel: siapkan **tabel kalibrasi huruf** Anda (dari Panduan Hardware bagian G) dan **nama + password WiFi 2.4GHz**, lalu tempel bersama prompt ini.

```
Kamu adalah insinyur firmware. Buatkan SATU file sketch Arduino (.ino) lengkap untuk ESP32 DevKit V1, untuk proyek sarung tangan penerjemah abjad jari (SIBI) bagi tuna wicara/tuna rungu.

KONTEKS HARDWARE:
- ESP32 DevKit V1, library ArduinoJson sudah terpasang.
- 5 sensor tekuk di pin analog ADC1: ibu jari=GPIO34, telunjuk=GPIO35, tengah=GPIO32, manis=GPIO33, kelingking=GPIO36. analogRead menghasilkan 0..4095; konversikan ke persen 0..100 dengan map().
- 2 tombol (INPUT_PULLUP, ditekan = LOW): SPASI=GPIO25, KIRIM=GPIO26.

CARA DETEKSI HURUF (lakukan di ESP32, jangan kirim data mentah ke server):
- Aku punya "kamus" pola tiap huruf dalam persen [ibujari, telunjuk, tengah, manis, kelingking]. Gunakan ini:
  A = [90,95,92,94,88]
  B = [10,8,7,9,6]
  C = [50,55,53,52,48]
  (CATATAN: ganti/ tambah baris di atas dengan tabel kalibrasi asliku yang kutempel di bawah.)
- Tiap loop: baca 5 sensor (persen), hitung jarak (selisih kuadrat) ke tiap huruf di kamus, pilih huruf dengan jarak TERKECIL.
- Hanya anggap valid bila jarak < AMBANG (buat konstanta yang mudah kuubah) DAN huruf yang sama stabil selama minimal 600 ms (debounce). Setelah satu huruf terkirim, jangan kirim huruf yang sama lagi sampai tangan berubah/ rileks.

PERILAKU TOMBOL:
- Tekan SPASI  -> kirim {aksi:"SPASI"}.
- Tekan KIRIM  -> kirim {aksi:"KIRIM"}.
- Tahan SPASI > 1 detik -> kirim {aksi:"HAPUS"} (hapus huruf terakhir).
- Beri debounce tombol ~50 ms.

KONEKSI & PENGIRIMAN:
- WiFi 2.4GHz: SSID dan PASSWORD jadikan konstanta di atas agar mudah kuubah.
- Kirim via HTTP POST JSON ke konstanta N8N_URL_HURUF (contoh "http://NGROK_ATAU_IP:5678/webhook/huruf"), header Content-Type: application/json.
- Body untuk huruf: {"device":"glove-01","aksi":"HURUF","huruf":"A"}. Untuk tombol: {"device":"glove-01","aksi":"SPASI"} dst.
- Tangani jika WiFi putus (coba sambung ulang) dan jika POST gagal (cetak kode error ke Serial, jangan crash).

OUTPUT & DEBUG:
- Serial 115200. Cetak huruf yang terdeteksi, aksi tombol, status WiFi, dan respons server agar mudah kupantau.
- Beri komentar berbahasa Indonesia yang jelas, dan tandai dengan jelas bagian KONSTANTA yang perlu kuubah (WiFi, URL, kamus huruf, AMBANG).

Tampilkan kode sebagai artifact yang bisa langsung kusalin ke Arduino IDE.

[TEMPEL TABEL KALIBRASI HURUF ASLIKU DI SINI]
[TEMPEL NAMA WIFI & PASSWORD DI SINI — atau tulis placeholder bila ingin isi sendiri]
```

**Output yang diharapkan:** satu artifact kode `.ino`.
**Cara tes:** upload ke ESP32 → buka Serial Monitor → bentuk huruf → harus muncul "Huruf terdeteksi: A" dst, dan respons dari n8n (setelah n8n siap di Prompt #2).

---

## ✅ PROMPT #2 — Workflow n8n (susun kalimat + panggil Claude)

**Tujuan:** dapat file **JSON workflow** yang bisa Anda **Impor** ke n8n.

```
Kamu ahli n8n. Buatkan SATU file JSON workflow n8n lengkap yang bisa langsung kuimpor (menu Import from File). Workflow ini untuk proyek penerjemah abjad jari: ESP32 mengirim huruf satu per satu, workflow merangkainya jadi kata/kalimat, lalu saat tombol KIRIM ditekan, memanggil Claude untuk merapikan ejaan & menyusun kalimat alami bahasa Indonesia. Dashboard web akan mengambil hasilnya.

GUNAKAN workflowStaticData (penyimpanan internal n8n) sebagai buffer — JANGAN pakai database eksternal.

BUAT DUA ALUR (boleh 2 workflow atau 1 workflow 2 trigger; jelaskan cara impornya):

ALUR 1 — Terima huruf:  Webhook (POST, path "huruf") -> Code node -> Respond to Webhook.
  Logika Code node (JavaScript):
  - Ambil staticData workflow: const s = $getWorkflowStaticData('global'); inisialisasi s.buffer = s.buffer || "" dan s.hasil = s.hasil || null.
  - Baca body: { aksi, huruf }.
    * aksi "HURUF" -> s.buffer += huruf
    * aksi "SPASI" -> s.buffer += " "
    * aksi "HAPUS" -> s.buffer = s.buffer.slice(0, -1)
    * aksi "KIRIM" -> set penanda perluProses=true (teks yang diproses = s.buffer)
  - Jika BUKAN "KIRIM": langsung kembalikan {ok:true, buffer:s.buffer, hasil:s.hasil} (tanpa memanggil Claude).
  - Jika "KIRIM": lanjut ke node Claude (di bawah), lalu simpan hasilnya ke s.hasil, KOSONGKAN s.buffer, dan balas {ok:true, buffer:"", hasil:s.hasil}.

  Node Claude (HTTP Request) — hanya dijalankan saat KIRIM:
  - POST https://api.anthropic.com/v1/messages
  - Header: x-api-key = (pakai credential / placeholder MASUKKAN_API_KEY), anthropic-version: 2023-06-01, content-type: application/json
  - Body JSON:
    {
      "model": "claude-haiku-4-5",
      "max_tokens": 300,
      "system": "Kamu memperbaiki hasil ejaan abjad jari bahasa Indonesia. Input berupa rangkaian huruf kapital yang mungkin salah/terpotong. Tugas: tebak kata/kalimat yang paling masuk akal dalam Bahasa Indonesia sehari-hari, perbaiki ejaan & spasi, beri kapitalisasi & tanda baca wajar. JANGAN menambah informasi yang tidak ada. Balas HANYA JSON valid tanpa teks lain: {\"teks\":\"...\",\"untuk_suara\":\"...\"} dengan untuk_suara = teks tanpa tanda baca berlebih agar enak dibacakan mesin.",
      "messages": [ { "role": "user", "content": "Rangkaian huruf: {{ buffer }}" } ]
    }
  - Parse balasan: ambil teks dari content[0].text, JSON.parse dengan try/catch (fallback {teks: bufferAsli, untuk_suara: bufferAsli}).

ALUR 2 — Status untuk dashboard:  Webhook (GET, path "status") -> Code node baca staticData -> Respond to Webhook JSON {buffer:s.buffer, hasil:s.hasil, ts:Date.now()}.

PERSYARATAN:
- Sertakan header CORS "Access-Control-Allow-Origin: *" pada Respond to Webhook (agar dashboard browser bisa akses).
- Tandai dengan jelas di mana aku memasukkan API key Claude.
- Beri penjelasan singkat langkah impor & cara mengaktifkan (Activate) workflow.
- Pastikan JSON workflow valid & lengkap (nodes + connections).

Tampilkan JSON sebagai artifact, plus instruksi impor singkat di bawahnya.
```

**Output yang diharapkan:** artifact JSON workflow + instruksi impor.
**Cara tes:** lihat file 03 bagian "Rencana Uji" (tes pakai `curl`).

---

## ✅ PROMPT #3 — Dashboard Web (subtitle + suara + dengar)

**Tujuan:** dapat satu file `.html` yang dibuka di tablet/HP/PC sebagai layar kios.

```
Kamu desainer & developer frontend. Buatkan SATU file HTML (HTML+CSS+JS dalam satu file, tanpa library eksternal) sebagai dashboard kios penerjemah isyarat untuk disabilitas. Harus jalan hanya dengan dibuka di browser (Chrome) di tablet/HP/PC.

FUNGSI:
1) SUBTITLE BESAR: setiap 1 detik, fetch GET ke URL n8n status (jadikan variabel N8N_STATUS_URL di atas, contoh "http://NGROK:5678/webhook/status").
   - Tampilkan "buffer" (kata yang sedang dirangkai) dengan font sedang, di bagian atas, sebagai indikator "sedang mengeja...".
   - Tampilkan "hasil.teks" (kalimat final dari Claude) dengan font SANGAT BESAR & kontras tinggi di tengah layar. Ini untuk TUNA RUNGU, jadi harus terbaca dari jarak jauh.
2) SUARA OTOMATIS (untuk TUNA NETRA & umum): saat "hasil.untuk_suara" BARU (berbeda dari sebelumnya), bacakan dengan Web Speech API (speechSynthesis), bahasa "id-ID". Jangan membacakan teks yang sama dua kali.
3) TOMBOL "🎤 Dengar Ucapan" (untuk TUNA RUNGU): pakai Web Speech API (SpeechRecognition / webkitSpeechRecognition) bahasa "id-ID" untuk mengubah ucapan lawan bicara menjadi teks, lalu tampilkan teks itu sebagai subtitle besar juga (boleh di panel terpisah berlabel "Lawan bicara:").
4) Kontrol kecil: tombol Mute/Unmute suara, slider kecepatan bicara, indikator status koneksi (terhubung/terputus ke n8n).

DESAIN (penting untuk aksesibilitas & kesan profesional untuk demo hibah):
- Kontras tinggi, teks besar, ramah low-vision. Mode gelap default. Hindari animasi mengganggu.
- Tata letak bersih, fokus pada area subtitle. Responsif (tablet & layar besar).
- Tambahkan judul kecil "SIBI-Bridge" dan ikon yang relevan.
- Tangani error fetch dengan anggun (tampilkan "Menyambung ulang..." bila gagal, jangan blank).

CATATAN TEKNIS:
- Tandai jelas variabel N8N_STATUS_URL yang harus kuisi.
- Web Speech API STT hanya jalan di Chrome via HTTPS atau localhost; sebutkan ini sebagai komentar.
- Jangan pakai localStorage/sessionStorage.

Tampilkan sebagai artifact HTML yang bisa langsung kubuka.
```

**Output yang diharapkan:** artifact `.html`.
**Cara tes:** buka di Chrome → harus menampilkan subtitle dummy/realtime & membacakan kalimat saat ada hasil baru.

---

## ✅ PROMPT #4 — Skrip Uji & Debug

**Tujuan:** alat untuk menguji pipeline **tanpa** harus menunggu hardware jadi.

```
Buatkan untukku alat uji untuk memverifikasi workflow n8n penerjemah isyarat (endpoint POST /webhook/huruf dan GET /webhook/status), dalam DUA bentuk:

1) Daftar perintah curl untuk Windows (PowerShell) yang:
   - mengirim huruf satu per satu (A, K, U, spasi, L, A, P, A, R),
   - lalu mengirim aksi KIRIM,
   - lalu membaca GET /webhook/status,
   sertakan contoh keluaran yang diharapkan di tiap langkah.

2) Satu file HTML "panel simulator" sederhana: tombol-tombol A–Z + tombol SPASI/HAPUS/KIRIM yang mengirim POST ke webhook n8n (variabel URL di atas), dan menampilkan balasan JSON. Ini mensimulasikan sarung tangan, jadi aku bisa menguji n8n + Claude + dashboard sebelum hardware siap.

Beri juga tabel "kasus uji" ringkas: input -> hasil yang diharapkan, termasuk kasus salah eja (mis. "AKKU" harus dirapikan jadi "Aku" oleh Claude) dan kasus HAPUS.

Jelaskan tiap langkah dengan bahasa Indonesia sederhana.
```

**Output yang diharapkan:** perintah curl + artifact HTML simulator + tabel kasus uji.

---

## 🔁 Prompt Tambahan (bila perlu)

**Kalau ada error**, tempel ke Claude:
```
Aku menjalankan [firmware ESP32 / workflow n8n / dashboard] yang kamu buat, lalu muncul error berikut. Tolong perbaiki dan jelaskan penyebabnya dengan bahasa sederhana.

[TEMPEL pesan error / isi Serial Monitor / screenshot teks error di sini]
[Sebutkan: langkah apa yang sedang kulakukan saat error muncul]
```

**Kalau ingin tambah fitur** (mis. OLED di sarung tangan, atau kata BISINDO dua tangan), jelaskan ke Claude apa yang Anda punya & inginkan; minta ia memberi versi revisi + apa yang berubah.

---

## Urutan Eksekusi yang Disarankan

1. **Prompt #2** (n8n) → impor & aktifkan workflow.
2. **Prompt #4** (simulator) → uji n8n + Claude **tanpa hardware**. Pastikan kalimat keluar rapi.
3. **Prompt #3** (dashboard) → sambungkan ke n8n, lihat subtitle & dengar suara.
4. **Prompt #1** (firmware) → setelah hardware & kalibrasi siap, sambungkan sarung tangan ke seluruh sistem.

> Dengan urutan ini, Anda bisa membuktikan **seluruh software jalan** lebih dulu (bagus untuk demo & laporan progres hibah), lalu hardware menyusul.
