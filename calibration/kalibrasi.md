# Kalibrasi Sensor — Nilai per Huruf (SIBI abjad jari)

> 👷 Diisi oleh Anda saat tahap **H6** (cara di `01-PANDUAN-HARDWARE.md` bagian G).
> 🤖 Claude Code **MEMBACA** file ini untuk membuat "kamus huruf" di firmware. **Jangan ditimpa otomatis.**
> Angka = persentase tekukan **0–100** (0 = jari lurus, 100 = tekuk penuh).
> Tombol fisik menangani **SPASI** & **KIRIM**, jadi tidak perlu gestur khusus untuk itu.

## Pengaturan
- **AMBANG** kecocokan (jarak maksimum agar huruf dianggap valid): `25` *(boleh diubah)*
- **Waktu stabil** sebelum huruf dikirim (debounce): `600` ms

## Tabel Pola Huruf
> Isi angka tiap kolom. Baris yang masih kosong akan **diabaikan** Claude Code saat membuat kamus.

| Huruf | Ibujari | Telunjuk | Tengah | Manis | Kelingking | Catatan |
|-------|---------|----------|--------|-------|------------|---------|
| A |  |  |  |  |  |  |
| B |  |  |  |  |  |  |
| C |  |  |  |  |  |  |
| D |  |  |  |  |  |  |
| E |  |  |  |  |  |  |
| F |  |  |  |  |  |  |
| G |  |  |  |  |  |  |
| H |  |  |  |  |  |  |
| I |  |  |  |  |  |  |
| J |  |  |  |  |  |  |
| K |  |  |  |  |  |  |
| L |  |  |  |  |  |  |
| M |  |  |  |  |  |  |
| N |  |  |  |  |  |  |
| O |  |  |  |  |  |  |
| P |  |  |  |  |  |  |
| Q |  |  |  |  |  |  |
| R |  |  |  |  |  |  |
| S |  |  |  |  |  |  |
| T |  |  |  |  |  |  |
| U |  |  |  |  |  |  |
| V |  |  |  |  |  |  |
| W |  |  |  |  |  |  |
| X |  |  |  |  |  |  |
| Y |  |  |  |  |  |  |
| Z |  |  |  |  |  |  |

## Tips
- Mulai isi **5–8 huruf** yang jelas berbeda dulu (mis. A, B, C, I, L, O, U, Y) untuk demo pertama.
- Lengkapi sisanya bertahap.
- Huruf **J** dan **Z** di abjad jari biasanya butuh gerakan — untuk Fase 0 boleh dilewati dulu atau dibuat versi statis.
- Setelah tabel terisi, minta Claude Code: *"Perbarui firmware pakai kamus terbaru di calibration/kalibrasi.md."*
