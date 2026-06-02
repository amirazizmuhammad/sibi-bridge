# 01 — Panduan Hardware (Fokus Anda) 🛠️

> ℹ️ **Catatan arah:** input PRIMER sekarang **kamera + MediaPipe** (`vision/`, tanpa solder). Panduan sarung tangan di bawah = jalur **alternatif/wearable** (opsional). Kerjakan hanya bila mau varian glove. Sumber kebenaran status: `CLAUDE.md` + `PROGRESS.md`.

> Tujuan: dari nol sampai sarung tangan bisa baca gerakan jari & kirim ke n8n. Ditulis untuk pemula tanpa latar belakang IoT, pengguna Windows.

---

## A. Pilih Dulu: Sensor Apa?

| Pilihan | Harga | Akurasi | Saran |
|---|---|---|---|
| **Velostat (DIY)** | ~Rp 60rb untuk 5+ sensor | Cukup baik | ✅ **Pilih ini** (sesuai budget) |
| Flex sensor asli (2.2") | ~Rp 80–150rb / buah | Sangat baik | Untuk Fase 1/2 bila ada dana |

Panduan ini memakai **Velostat** karena sesuai budget Rp 200–500rb. Cara kerjanya sama-sama: tekukan jari mengubah hambatan listrik → ESP32 membacanya sebagai angka.

---

## B. Daftar Belanja (Bill of Materials)

### Versi Hemat — Velostat DIY (~Rp 250rb)

| No | Komponen | Jumlah | Estimasi Harga | Catatan |
|---|---|---|---|---|
| 1 | ESP32 DevKit V1 (38 pin) | 1 | Rp 45.000 | Otak + WiFi sudah jadi satu |
| 2 | Lembaran Velostat (A4) | 1 | Rp 60.000 | Bahan sensor tekuk, cukup untuk banyak |
| 3 | Lakban tembaga (copper tape) | 1 rol | Rp 30.000 | Kontak listrik sensor |
| 4 | Resistor 10kΩ | 6 | Rp 5.000 | 5 untuk sensor + cadangan |
| 5 | Push button kecil (tactile) | 2 | Rp 4.000 | Tombol **Spasi** & **Kirim** |
| 6 | Breadboard 400 titik | 1 | Rp 25.000 | Untuk merangkai tanpa solder |
| 7 | Kabel jumper (male-male & male-female) | 1 set | Rp 25.000 | Penghubung |
| 8 | Sarung tangan kain/karet tipis | 1 | Rp 15.000 | Tempat menempel sensor |
| 9 | Kabel data Micro-USB | 1 | Rp 15.000 | **Pastikan kabel DATA, bukan charge-only** |
| 10 | Solder + timah (opsional) | 1 | Rp 30.000 | Bila ingin sambungan permanen |
| | **TOTAL** | | **± Rp 254.000** | |

> 💡 Beli ESP32 **DevKit V1 38-pin** (paling umum & banyak tutorialnya). Hindari yang 30-pin untuk pemula.

### Tambahan Opsional (Fase 1)
| Komponen | Harga | Guna |
|---|---|---|
| OLED 0.96" I2C | Rp 30.000 | Lihat huruf yang sedang dibentuk |
| Speaker mini + modul PAM8403 | Rp 35.000 | Suara mandiri (kalau tak pakai tablet) |
| Power bank | Rp 80.000 | Alat portabel |

---

## C. Memahami Rangkaian (Voltage Divider)

Setiap sensor tekuk **tidak bisa langsung** dibaca ESP32. Kita pasang **resistor 10kΩ** membentuk "pembagi tegangan". Polanya untuk **tiap** sensor:

```
   3V3 ──────[ SENSOR TEKUK ]──────●──────[ Resistor 10kΩ ]────── GND
                                    │
                                    └────── ke pin analog ESP32 (mis. GPIO34)
```

- Jari **lurus** → hambatan sensor kecil → tegangan di titik ● tinggi → angka besar.
- Jari **tekuk** → hambatan sensor besar → tegangan di titik ● rendah → angka kecil.

(Arah besar/kecil tidak masalah — nanti dikalibrasi.)

### Peta Pin ESP32 (PENTING — sumber error tersering!)

⚠️ Saat WiFi menyala, pin **ADC2 mati**. **Wajib** pakai pin **ADC1** berikut:

| Jari | Pin ESP32 | Tipe |
|---|---|---|
| Ibu jari (Thumb) | **GPIO 34** | ADC1 (input-only) ✅ |
| Telunjuk (Index) | **GPIO 35** | ADC1 (input-only) ✅ |
| Tengah (Middle) | **GPIO 32** | ADC1 ✅ |
| Manis (Ring) | **GPIO 33** | ADC1 ✅ |
| Kelingking (Pinky) | **GPIO 36 (VP)** | ADC1 (input-only) ✅ |
| Tombol SPASI | **GPIO 25** | Digital (boleh) |
| Tombol KIRIM | **GPIO 26** | Digital (boleh) |

> ❌ JANGAN pakai GPIO 0, 2, 4, 12, 13, 14, 15, 25, 26, 27 untuk **sensor analog** (itu ADC2 / pin khusus). GPIO 25 & 26 di sini dipakai untuk **tombol digital** saja, bukan sensor analog — itu aman.

### Wiring tombol (push button)
```
  GPIO25 ──[ tombol ]── GND      (pakai INPUT_PULLUP di kode; ditekan = LOW)
  GPIO26 ──[ tombol ]── GND
```

---

## D. Cara Membuat Sensor Tekuk dari Velostat (DIY)

Ulangi **5×** (satu per jari). Tiap sensor butuh ~7 cm.

1. **Potong Velostat**: 1 strip ukuran ± 1,5 cm × 6 cm.
2. **Potong 2 strip lakban tembaga**: masing-masing ± 0,8 cm × 7 cm.
3. **Susun berlapis (sandwich):**
   ```
   [ lakban tembaga A ]  ← kabel ke 3V3 / ke pin
   [ ===== VELOSTAT ===== ]
   [ lakban tembaga B ]  ← kabel ke resistor
   ```
   Tembaga A dan B **tidak boleh bersentuhan langsung** — harus dipisah Velostat.
4. **Solder/jepit kabel** ke tiap lakban tembaga (sisakan ujung tembaga di luar untuk kabel).
5. **Bungkus** seluruh sandwich dengan selotip bening agar rapat & tahan lama.
6. **Tes cepat** pakai multimeter (mode Ohm): saat ditekuk, angka hambatan harus **berubah**. Kalau tidak berubah → tembaga mungkin bersentuhan, ulangi.
7. **Tempel** di punggung tiap jari sarung tangan (pakai lem kain/jahit), posisi sensor pas di sendi jari agar menekuk saat jari ditekuk.

> Tips: lapisi lagi bagian luar dengan kain/isolasi agar tidak korslet saat dipakai.

---

## E. Setup Software di Windows (sekali saja)

Anda perlu **Arduino IDE** hanya untuk meng-upload kode (yang dibuatkan Claude) ke ESP32.

1. **Unduh Arduino IDE 2.x** dari `https://www.arduino.cc/en/software` → install.
2. **Tambahkan dukungan ESP32:**
   - Buka Arduino IDE → menu **File → Preferences**.
   - Di kolom *Additional Boards Manager URLs*, tempel:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - **Tools → Board → Boards Manager** → cari **esp32** → Install (oleh Espressif).
3. **Driver USB** (agar ESP32 terdeteksi):
   - Kebanyakan ESP32 pakai chip **CP2102** atau **CH340**.
   - Jika colok ESP32 tapi tak muncul port COM baru → install driver:
     - CP2102: cari "CP210x VCP driver Silicon Labs".
     - CH340: cari "CH340 driver Windows".
4. **Pasang library** (Sketch → Include Library → Manage Libraries), cari & install:
   - **ArduinoJson** (oleh Benoit Blanchon)

> Setelah ini Anda **tidak perlu menulis kode sendiri** — cukup tempel kode dari Claude (prompt #1), pilih board "ESP32 Dev Module", pilih port COM, klik **Upload (→)**.

---

## F. Tes Hardware Mandiri (Tanpa n8n/Claude dulu)

Sebelum menyambung ke internet, pastikan **sensor & tombol terbaca**. Tempel kode tes ini ke Arduino IDE, upload, lalu buka **Tools → Serial Monitor** (baud **115200**).

```cpp
// ===== TES SENSOR & TOMBOL (hardware only) =====
const int PINS[5] = {34, 35, 32, 33, 36};   // thumb, index, middle, ring, pinky
const char* NAMA[5] = {"Ibujari","Telunjuk","Tengah","Manis","Kelingking"};
const int BTN_SPASI = 25;
const int BTN_KIRIM = 26;

void setup() {
  Serial.begin(115200);
  pinMode(BTN_SPASI, INPUT_PULLUP);
  pinMode(BTN_KIRIM, INPUT_PULLUP);
  Serial.println("\n== Tes Hardware Dimulai ==");
}

void loop() {
  Serial.print("Sensor -> ");
  for (int i = 0; i < 5; i++) {
    int nilai = analogRead(PINS[i]);          // 0..4095
    int persen = map(nilai, 0, 4095, 0, 100); // 0..100
    Serial.printf("%s:%d%%  ", NAMA[i], persen);
  }
  Serial.printf("| SPASI:%s KIRIM:%s\n",
    digitalRead(BTN_SPASI) == LOW ? "DITEKAN" : "-",
    digitalRead(BTN_KIRIM) == LOW ? "DITEKAN" : "-");
  delay(300);
}
```

**Yang harus Anda lihat:**
- Angka tiap jari **berubah** saat ditekuk/diluruskan. ✅
- Saat tombol ditekan, statusnya jadi **DITEKAN**. ✅

Kalau angka diam saja / selalu 0 atau 100 → cek bagian **G. Troubleshooting**.

---

## G. Kalibrasi (Rekam Pola Tiap Huruf)

Setelah hardware terbukti jalan, Anda perlu **merekam pola angka** untuk tiap huruf A–Z. Inilah "kamus" yang dipakai ESP32 untuk mengenali huruf.

**Cara praktis (manual dulu):**
1. Jalankan kode tes di atas.
2. Bentuk tangan huruf **A** (kepalan), catat 5 angkanya. Contoh: `A = 90, 95, 92, 94, 88`.
3. Ulangi untuk B, C, … Z. Catat di tabel:

| Huruf | Ibujari | Telunjuk | Tengah | Manis | Kelingking |
|---|---|---|---|---|---|
| A | 90 | 95 | 92 | 94 | 88 |
| B | 10 | 8 | 7 | 9 | 6 |
| C | 50 | 55 | 53 | 52 | 48 |
| … | | | | | |

4. Serahkan tabel ini ke Claude (lihat prompt #1) → Claude memasukkannya ke firmware sebagai "kamus huruf". ESP32 lalu mencocokkan pembacaan dengan kamus (cari yang paling mirip).

> 💡 **Tidak perlu rekam semua 26 huruf sekaligus.** Mulai dari 5–8 huruf yang berbeda jelas (mis. A, B, C, I, L, O, U, Y) untuk demo pertama. Tambah sisanya kemudian. Abjad jari SIBI satu tangan — referensi posisi tangannya bisa Anda cari di panduan SIBI/abjad jari resmi.

---

## H. Troubleshooting

| Masalah | Kemungkinan Sebab | Solusi |
|---|---|---|
| Port COM tak muncul | Driver belum ada / kabel charge-only | Install driver CP2102/CH340; ganti kabel **data** |
| Upload gagal / "Connecting…" | ESP32 tak masuk mode flash | Saat muncul "Connecting", **tahan tombol BOOT** di ESP32 |
| Semua sensor baca 0 atau 4095 | Sensor korslet / kabel lepas / pakai pin ADC2 | Pastikan pin **34/35/32/33/36**; cek sandwich Velostat |
| Angka sensor acak/loncat-loncat | Kabel longgar / tanpa resistor | Pastikan resistor 10kΩ terpasang & kabel rapat |
| WiFi tak konek (nanti) | SSID/password salah / WiFi 5GHz | ESP32 hanya **2.4GHz**; pakai WiFi 2.4GHz |
| Tombol selalu "DITEKAN" | Lupa `INPUT_PULLUP` / salah wiring | Tombol ke **GND**, kode pakai `INPUT_PULLUP` |
| ESP32 sering restart | Daya kurang dari USB laptop | Pakai port USB lain / power bank / adaptor 5V |

---

## I. Checklist Sebelum Lanjut ke Software

- [ ] ESP32 terdeteksi di Arduino IDE (port COM muncul)
- [ ] Kode tes ter-upload & Serial Monitor jalan
- [ ] 5 sensor angkanya berubah saat jari ditekuk
- [ ] 2 tombol terbaca DITEKAN
- [ ] Sudah rekam pola minimal 5–8 huruf
- [ ] Tahu nama WiFi 2.4GHz & passwordnya

Kalau semua ✅ → buka `02-PROMPT-UNTUK-CLAUDE.md`, tempel **Prompt #1** ke Claude untuk dapat firmware lengkap (deteksi huruf + kirim ke n8n).
