# Folder: n8n/

🤖 Claude Code sudah membuat `workflow-isyarat.json` di sini (Tugas S1).
👷 Anda tinggal impor & aktifkan.

## Cara Impor (langkah singkat)
1. Buka n8n → pojok kanan atas **⋯** → **Import from File** → pilih `workflow-isyarat.json`.
2. Buka node **Panggil Claude** → header `Authorization` → ganti `Bearer MASUKKAN_API_KEY` dengan `Bearer <API key sumopod Anda>`.
   - Endpoint sudah disetel ke **sumopod AI** (`https://ai.sumopod.com/v1/chat/completions`, proxy LiteLLM, format OpenAI). BUKAN api.anthropic.com.
   - Cara lebih rapi: buat **Credentials → Header Auth** (Name `Authorization`, Value `Bearer <key>`) lalu pakai di node.
   - **Cek nama model**: di node `Proses Huruf` ada `const MODEL_AI = "claude-haiku-4-5"`. Pastikan cocok dengan model di sumopod Anda. Cek daftar model:
     ```powershell
     curl.exe -s https://ai.sumopod.com/v1/models -H "Authorization: Bearer <KEY>"
     ```
3. Klik **Active** (toggle kanan atas) agar webhook hidup.
4. Catat URL webhook (Production) yang muncul:
   - `POST .../webhook/huruf`
   - `GET  .../webhook/status`
5. Jika perlu diakses dari HP/ESP32: jalankan **ngrok** (`ngrok http 5678`) — lihat bagian D di file 03.

## Isi Workflow (10 node)
- **Webhook Huruf** (POST `huruf`) → **Proses Huruf** (Code, rangkai buffer di `workflowStaticData`) → **Perlu Panggil Claude?** (IF).
  - Bukan `KIRIM` / buffer kosong → **Balas Huruf** (`{ok,buffer,hasil}`).
  - `KIRIM` + buffer berisi → **Panggil Claude** (HTTP ke sumopod AI, model `claude-haiku-4-5`, `max_tokens` 300) → **Simpan Hasil** (parse `choices[0].message.content` + fallback offline, kosongkan buffer) → **Balas KIRIM**.
- **Webhook Status** (GET `status`) → **Baca Status** (Code) → **Balas Status** (`{buffer,hasil,ts}`).

## Catatan teknis
- CORS: tiap Webhook punya opsi `allowedOrigins: *` (menangani preflight OPTIONS) + tiap Respond menambah header `Access-Control-Allow-Origin: *`. Jadi dashboard & simulator browser bisa akses.
- **Claude dipanggil 1× per kalimat** (hanya saat `KIRIM`), bukan tiap huruf → hemat biaya.
- **Mode offline / aman**: bila Claude gagal atau format JSON tidak sesuai, `Simpan Hasil` memakai buffer apa adanya (`{teks, untuk_suara}` = buffer). Tidak crash.
- **Privasi**: `buffer` dikosongkan tiap kalimat selesai (di `Simpan Hasil`).
- **AI via sumopod** (`https://ai.sumopod.com/v1` = proxy LiteLLM, format OpenAI). Body = `{model, max_tokens, temperature, messages:[system,user]}`. Balasan dibaca dari `choices[0].message.content` lalu `JSON.parse`. Nama model diatur di `const MODEL_AI` (node Proses Huruf).

## Uji cepat (curl PowerShell)
Lihat `tools/uji-curl.md` (Tugas S2) untuk perintah uji lengkap + tabel kasus uji.
