# 04 — Kerangka Proposal Hibah & Pemanfaatan Smart City 📑

> Kerangka siap-isi untuk proposal hibah. Bagian **[ISI: ...]** perlu Anda lengkapi. Angka RAB & statistik bersifat ilustrasi — **verifikasi dari sumber resmi** (daftar di bagian akhir) sebelum diajukan.

---

## 1. Identitas Usulan

- **Judul:** SIBI-Bridge: Jembatan Komunikasi Inklusif untuk Tuna Rungu, Tuna Wicara, dan Tuna Netra berbasis IoT & Kecerdasan Buatan
- **Pengusul:** [ISI: nama/tim/institusi]
- **Bidang:** Teknologi Asistif / Smart Society / Inklusi Disabilitas
- **Skema hibah dituju:** [ISI: lihat bagian 14]

---

## 2. Ringkasan Eksekutif (1 paragraf)

SIBI-Bridge adalah perangkat layanan publik berbiaya rendah yang menerjemahkan bahasa isyarat (abjad jari SIBI) menjadi teks dan suara secara langsung, serta mengubah ucapan menjadi teks. Dengan satu alat, tiga kelompok disabilitas terlayani sekaligus: tuna wicara dapat "bersuara", tuna rungu dapat "membaca" percakapan, dan tuna netra dapat "mendengar" pesan. Dibangun dengan IoT (mikrokontroler + sensor), orkestrasi n8n, dan kecerdasan buatan Claude untuk menyusun kalimat alami, solusi ini dirancang untuk ditempatkan di kios layanan publik kota cerdas (kelurahan, puskesmas, transportasi) guna mewujudkan kota yang **inklusif dan setara**.

---

## 3. Latar Belakang & Urgensi

- Penyandang disabilitas di Indonesia menghadapi hambatan akses informasi & layanan publik. Catatan resmi menunjukkan **kesenjangan data** dan keterbatasan akses layanan bagi kelompok ini.
- Komunikasi tatap muka di loket layanan publik (kelurahan, RS, bank, transportasi) masih bergantung pada petugas yang umumnya **tidak menguasai bahasa isyarat**, sehingga tuna rungu/tuna wicara kerap kesulitan.
- Solusi penerjemah yang ada sering **mahal/impor** atau berbasis kamera yang butuh perangkat tinggi. Dibutuhkan solusi **murah, lokal, dan mudah direplikasi**.
- [ISI: tambahkan data jumlah penyandang tuna rungu/wicara/netra di wilayah Anda dari sumber resmi — lihat bagian 15. Sertakan sumber & tahun.]

---

## 4. Rumusan Masalah

1. Bagaimana menyediakan penerjemah bahasa isyarat ↔ teks ↔ suara yang **terjangkau** untuk layanan publik?
2. Bagaimana satu perangkat dapat melayani **tiga kelompok** disabilitas sekaligus?
3. Bagaimana memastikan solusi **mudah dirawat & direplikasi** oleh pemerintah daerah?

---

## 5. Tujuan & Manfaat

**Tujuan umum:** mewujudkan akses komunikasi setara di ruang publik kota cerdas.

**Tujuan khusus:**
- Membangun prototipe penerjemah abjad jari → kalimat (teks + suara).
- Menambahkan jalur ucapan → teks untuk tuna rungu.
- Menguji akurasi, latensi, & kepuasan pengguna di lapangan.

**Manfaat:**
- *Sosial:* kemandirian & martabat penyandang disabilitas; layanan publik inklusif.
- *Pemerintah:* dukungan SDGs (poin 10 & 11), implementasi UU No. 8/2016 tentang Penyandang Disabilitas, indikator kota inklusif.
- *Ekonomi:* biaya per unit rendah, hemat operasional (AI dipanggil hemat).

---

## 6. Inovasi & Kebaruan

| Aspek | Solusi Umum | SIBI-Bridge |
|---|---|---|
| Cakupan pengguna | Satu kelompok | **Tiga kelompok** dalam satu alat |
| Biaya | Tinggi/impor | **Rendah, komponen lokal & DIY** |
| Kecerdasan | Pencocokan kaku | **AI menyusun kalimat alami & koreksi ejaan** |
| Arsitektur | Tertutup | **Modular & dapat direplikasi (low-code n8n)** |
| Ketahanan | Bergantung server | **Deteksi lokal + mode offline** |

Kebaruan utama: **deteksi isyarat di perangkat (cepat & murah) + AI hanya untuk penyusunan kalimat**, sehingga real-time, hemat, dan tetap berjalan saat jaringan lemah.

---

## 7. Keterkaitan dengan Smart City

Mendukung pilar **Smart Society** & **Smart Living** dalam kerangka kota cerdas:
- Layanan publik inklusif & ramah disabilitas.
- Pemerataan akses informasi.
- Dapat diintegrasikan ke kios/anjungan layanan kelurahan, dinas, dan fasilitas publik.
- [ISI: kaitkan dengan masterplan/rencana Smart City kota Anda bila ada.]

---

## 8. Studi Kasus Penempatan (Use Case)

| Lokasi | Manfaat Nyata |
|---|---|
| Kantor kelurahan/kecamatan | Warga tuli mengurus surat tanpa pendamping |
| Puskesmas / RS | Pasien tuna wicara menyampaikan keluhan ke perawat |
| Halte/stasiun/terminal | Informasi & bantuan untuk semua disabilitas |
| Bank / loket BUMD | Transaksi mandiri yang setara |
| Sekolah luar biasa (SLB) | Alat bantu belajar & latihan komunikasi |

---

## 9. Metodologi & Tahapan

1. **Analisis kebutuhan** bersama komunitas (Gerkatin, Pertuni) & dinas terkait.
2. **Perancangan & prototipe** (Fase 0): hardware + n8n + Claude + dashboard.
3. **Uji laboratorium**: akurasi, latensi (lihat kasus uji di file 03).
4. **Uji lapangan terbatas** (pilot) di 1–2 lokasi, dengan pengguna nyata.
5. **Evaluasi & iterasi** berdasarkan umpan balik & data.
6. **Diseminasi & rencana replikasi**.

Tingkat Kesiapterapan Teknologi (TKT/TRL) target: dari **TRL 3–4** (prototipe lab) menuju **TRL 6–7** (purwarupa teruji di lingkungan relevan) pada akhir program.

---

## 10. Rencana Anggaran Biaya (RAB) — Ilustrasi

### Tahap Prototipe (Fase 0)
| Item | Qty | Satuan | Jumlah |
|---|---|---|---|
| ESP32 + sensor + tombol + bahan sarung tangan | 2 set | Rp 300.000 | Rp 600.000 |
| Tablet/layar untuk dashboard | 1 | Rp 1.500.000 | Rp 1.500.000 |
| Speaker | 1 | Rp 150.000 | Rp 150.000 |
| Kredit API Claude (uji) | — | — | Rp 500.000 |
| Langganan ngrok/hosting (uji) | — | — | Rp 300.000 |
| **Subtotal Prototipe** | | | **Rp 3.050.000** |

### Tahap Pilot (Fase 1) — per 3 unit kios
| Item | Qty | Satuan | Jumlah |
|---|---|---|---|
| Unit kios lengkap (alat+tablet+speaker+casing) | 3 | Rp 2.500.000 | Rp 7.500.000 |
| Casing/enclosure & instalasi | 3 | Rp 500.000 | Rp 1.500.000 |
| Operasional API + jaringan (6 bln) | — | — | Rp 1.500.000 |
| Pelatihan petugas & sosialisasi | — | — | Rp 2.000.000 |
| Dokumentasi, video, evaluasi | — | — | Rp 2.500.000 |
| **Subtotal Pilot** | | | **Rp 15.000.000** |

> [ISI: sesuaikan dengan plafon hibah & jumlah unit. Tambahkan honor tim, perjalanan, dll sesuai format pemberi hibah.]

---

## 11. Jadwal Pelaksanaan (Timeline)

| Bulan | Kegiatan |
|---|---|
| 1 | Analisis kebutuhan, pengadaan komponen |
| 2 | Bangun prototipe (hardware + software) |
| 3 | Uji lab (akurasi, latensi), perbaikan |
| 4 | Uji lapangan terbatas + umpan balik komunitas |
| 5 | Iterasi & penambahan fitur (STT, casing) |
| 6 | Evaluasi, laporan, diseminasi |

---

## 12. Indikator Keberhasilan (KPI)

| Indikator | Target |
|---|---|
| Akurasi pengenalan huruf | > 80% (prototipe) → > 90% (pilot) |
| Latensi isyarat → kalimat tersuara | < 3 detik |
| Jumlah huruf SIBI dikenali | ≥ 26 (abjad jari) |
| Pengguna uji coba | ≥ [ISI] orang |
| Skor kepuasan pengguna (skala 1–5) | ≥ 4 |
| Unit kios terpasang (pilot) | ≥ [ISI] |
| Biaya operasional AI per kalimat | < Rp [ISI] (sangat rendah) |

---

## 13. Etika & Privasi Data ⚖️ (jangan dilewati!)

Penilai hibah & regulasi sangat memperhatikan ini. Suara dan gerakan pengguna adalah **data pribadi**.

- **Dasar hukum:** UU No. 27/2022 tentang Pelindungan Data Pribadi (PDP).
- **Prinsip yang diterapkan:**
  - *Minimal data:* hanya proses huruf/kalimat seperlunya; **jangan simpan** rekaman suara/biometrik tanpa perlu.
  - *Persetujuan (consent):* tampilkan pemberitahuan & minta persetujuan sebelum memproses ucapan.
  - *Transparansi:* kebijakan privasi singkat di kios.
  - *Keamanan:* API key dijaga; komunikasi via HTTPS; tidak menampilkan data sensitif di URL.
  - *Tanpa pengenalan wajah/biometrik* yang tidak perlu.
- **Catatan teknis:** sistem ini **tidak menyimpan** percakapan secara default (buffer dikosongkan tiap kalimat). Tegaskan ini sebagai keunggulan privasi.

---

## 14. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Akurasi sensor rendah | Salah terjemah | Kalibrasi per pengguna; AI koreksi; debounce |
| Variasi isyarat antar orang | Tidak konsisten | Mode kalibrasi personal; kumpulkan data |
| Jaringan tidak stabil | Layanan terganggu | Mode offline (tampil tanpa AI) |
| Biaya API membengkak | Operasional naik | Haiku 4.5 + caching + panggil per kalimat |
| Penolakan/komunitas tak dilibatkan | Solusi tak relevan | Libatkan Gerkatin/Pertuni sejak awal |
| Ketergantungan 1 vendor AI | Risiko keberlanjutan | Arsitektur modular; AI bisa diganti |

---

## 15. Keberlanjutan

- **Biaya per unit rendah** & komponen lokal → mudah direplikasi pemda lain.
- **Open-source** (dokumentasi + workflow) agar institusi lain dapat mengadopsi.
- **Model perawatan:** panduan + pelatihan petugas; suku cadang mudah didapat.
- **Pengembangan bertahap:** dari abjad jari → kata/kalimat BISINDO (Fase 2).
- **Potensi kemitraan/pendanaan lanjutan:** CSR, dinas, kampus.

---

## 16. Mitra Potensial

- **Komunitas disabilitas:** Gerkatin (komunitas Tuli), Pertuni (Persatuan Tunanetra Indonesia) — untuk validasi & uji pengguna.
- **Pemerintah:** Dinas Sosial, Diskominfo (Smart City), kelurahan/kecamatan.
- **Akademik:** kampus/lab teknik & pendidikan luar biasa (SLB) untuk uji & riset.
- **Pendukung:** komunitas maker/IoT lokal, CSR perusahaan.

> Lampirkan **surat dukungan/komitmen** dari minimal satu mitra — sangat memperkuat proposal.

---

## 17. Skema Hibah yang Relevan (untuk ditelusuri)

[ISI: cek kelayakan & jadwal masing-masing — daftar ini sebagai titik awal pencarian, bukan jaminan.]
- Hibah/riset Kemendikbudristek (mis. program inovasi/kewirausahaan mahasiswa, matching fund/Kedaireka bila ada mitra industri).
- Program inovasi BRIN / riset disabilitas.
- Program/CSR korporasi bidang inklusi & teknologi.
- Hibah pemerintah daerah / Smart City Diskominfo.
- Kompetisi inovasi sosial & teknologi asistif (nasional/internasional).

---

## 18. Lampiran: Sumber Data Resmi (untuk statistik proposal)

Gunakan ini untuk mengisi angka di bagian 3 & 12 dengan data **terverifikasi**:
- **Badan Pusat Statistik (BPS)** — Survei Sosial Ekonomi Nasional (Susenas), data disabilitas. `bps.go.id`
- **Kementerian Sosial** — Sistem data penyandang disabilitas. `kemensos.go.id`
- **Satu Data Indonesia** — `data.go.id` dan `katalog.satudata.go.id` (dataset jumlah disabilitas per jenis & tahun).
- **Pemda setempat** — Dinas Sosial provinsi/kota (data lokal paling relevan untuk lokasi pilot).
- **PBB/UNICEF Indonesia** — laporan analisis data disabilitas (konteks kesenjangan data).

> Praktik baik: selalu tulis **(Sumber: nama lembaga, tahun)** di bawah setiap angka pada proposal final.

---

*Susun naskah final sesuai template resmi pemberi hibah (sistematika, batas halaman, lampiran). Sesuaikan RAB dengan plafon & komponen biaya yang diperbolehkan.*
