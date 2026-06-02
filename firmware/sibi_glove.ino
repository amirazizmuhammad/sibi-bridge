/*
 * ============================================================================
 *  SIBI-Bridge — Firmware Sarung Tangan Penerjemah Abjad Jari (Tugas S4)
 *  Board : ESP32 DevKit V1
 *  Library: WiFi, HTTPClient (bawaan ESP32) + ArduinoJson (pasang via Library Manager)
 * ----------------------------------------------------------------------------
 *  Tugas: baca 5 sensor tekuk + 2 tombol -> kenali huruf dari kamus kalibrasi
 *         -> kirim ke n8n (POST /webhook/huruf). Deteksi dilakukan DI ESP32
 *         (kirim huruf, BUKAN data mentah).
 *
 *  >>> BAGIAN YANG PERLU ANDA UBAH ditandai dengan "UBAH:" <<<
 *  1. WIFI_SSID / WIFI_PASS         (WiFi 2.4 GHz)
 *  2. N8N_URL_HURUF                 (URL webhook n8n; sudah diisi ke VPS sumopod)
 *  3. KAMUS HURUF                   (salin dari calibration/kalibrasi.md)
 *  4. AMBANG / STABIL_MS            (sudah diisi dari kalibrasi.md, boleh disetel)
 * ============================================================================
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================ KONSTANTA (UBAH) ==============================

// UBAH: WiFi 2.4 GHz (ESP32 tidak mendukung 5 GHz)
const char* WIFI_SSID = "GANTI_NAMA_WIFI";
const char* WIFI_PASS = "GANTI_PASSWORD_WIFI";

// URL webhook n8n — SUDAH diisi ke VPS sumopod milikmu (UBAH bila pindah server).
const char* N8N_URL_HURUF = "https://n8n-kks2xqcv5bbm.jkt5.sumopod.my.id/webhook/huruf";

const char* DEVICE_ID = "glove-01"; // identitas sarung tangan (sesuai kontrak data)

// Token keamanan — UBAH: harus sama persis dengan SIBI_SECRET di n8n (node Proses Huruf)
// dan SIBI_TOKEN di vision/sibi_common.py. Kosongkan ("") untuk menonaktifkan.
const char* SIBI_TOKEN = "";

// --- Ambang & debounce (UBAH: nilai awal dari calibration/kalibrasi.md) ---
// AMBANG = jarak Euclidean maksimum (dalam satuan persen) agar huruf dianggap cocok.
// Makin kecil = makin ketat. Default 25 (dari kalibrasi.md). Naikkan bila sulit kena.
const float AMBANG = 25.0;
// Huruf harus stabil minimal sekian milidetik sebelum dikirim (anti getar).
const unsigned long STABIL_MS = 600;

// --- Pin sensor tekuk: HANYA ADC1 (ADC2 mati saat WiFi aktif) ---
const int PIN_IBUJARI    = 34; // thumb
const int PIN_TELUNJUK   = 35; // index
const int PIN_TENGAH     = 32; // middle
const int PIN_MANIS      = 33; // ring
const int PIN_KELINGKING = 36; // pinky
const int PIN_SENSOR[5]  = { PIN_IBUJARI, PIN_TELUNJUK, PIN_TENGAH, PIN_MANIS, PIN_KELINGKING };

// --- Pin tombol (INPUT_PULLUP, ditekan = LOW) ---
const int PIN_SPASI = 25;
const int PIN_KIRIM = 26;

// Pengaturan tombol
const unsigned long DEBOUNCE_TOMBOL_MS = 50;   // anti pantul ~50 ms
const unsigned long TAHAN_HAPUS_MS     = 1000; // tahan SPASI > 1 dtk -> HAPUS

// ===========================================================================
//  KAMUS HURUF  ===  UBAH: GANTI dengan tabel dari calibration/kalibrasi.md  ===
// ---------------------------------------------------------------------------
//  Format: { 'HURUF', { ibujari, telunjuk, tengah, manis, kelingking } }  (persen 0..100)
//
//  >>> NILAI DI BAWAH HANYA CONTOH/PLACEHOLDER <<<
//  Saat ini calibration/kalibrasi.md masih KOSONG. Setelah Anda rekam pola jari
//  (tahap H6), salin angkanya ke sini, lalu minta Claude Code:
//  "Perbarui firmware pakai kamus terbaru di calibration/kalibrasi.md."
// ===========================================================================
struct PolaHuruf {
  char ch;
  int  pola[5];
};
PolaHuruf kamus[] = {
  { 'A', { 90, 95, 92, 94, 88 } },  // CONTOH — ganti dgn nilai asli
  { 'B', { 10,  8,  7,  9,  6 } },  // CONTOH — ganti dgn nilai asli
  { 'C', { 50, 55, 53, 52, 48 } },  // CONTOH — ganti dgn nilai asli
};
const int JUM_HURUF = sizeof(kamus) / sizeof(kamus[0]);

// =============================== STATE GLOBAL ==============================
char  hurufTerkirim   = 0;   // huruf yg sedang "ditahan" (jangan kirim ulang sampai tangan rileks)
char  kandidatTerakhir= 0;   // huruf kandidat pada loop sebelumnya
unsigned long mulaiStabil = 0;

// State tombol SPASI (perlu bedakan tap vs tahan)
bool spasiSedangDitekan = false;
bool spasiHoldTerkirim  = false;
unsigned long spasiMulai = 0;

// =============================== FUNGSI WIFI ===============================
void hubungkanWiFi() {
  Serial.printf("[WiFi] Menyambung ke %s ...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) {
    delay(300);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Terhubung. IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WiFi] GAGAL menyambung (akan dicoba ulang otomatis). Lanjut mode offline.");
  }
}

// Jaga koneksi: bila putus, coba sambung ulang tanpa membuat sketch macet total.
void jagaWiFi() {
  static unsigned long terakhirCoba = 0;
  if (WiFi.status() != WL_CONNECTED && millis() - terakhirCoba > 5000) {
    terakhirCoba = millis();
    Serial.println("[WiFi] Terputus, mencoba sambung ulang...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  }
}

// =============================== PENGIRIMAN ================================
// Kirim 1 kejadian ke n8n. huruf="" untuk aksi tombol.
void kirimKeServer(const char* aksi, const char* huruf) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[POST] Dilewati (offline): aksi=%s huruf=%s\n", aksi, huruf);
    return;
  }
  HTTPClient http;
  http.setConnectTimeout(4000);
  http.setTimeout(6000);
  // Dukung HTTPS (sumopod) maupun HTTP lokal.
  WiFiClientSecure clientSecure; clientSecure.setInsecure(); // lewati validasi sertifikat (cukup utk Fase 0)
  WiFiClient clientPlain;
  if (String(N8N_URL_HURUF).startsWith("https")) { http.begin(clientSecure, N8N_URL_HURUF); }
  else { http.begin(clientPlain, N8N_URL_HURUF); }
  http.addHeader("Content-Type", "application/json");
  if (strlen(SIBI_TOKEN) > 0) { http.addHeader("X-SIBI-Token", SIBI_TOKEN); }

  StaticJsonDocument<128> doc;
  doc["device"] = DEVICE_ID;
  doc["aksi"]   = aksi;
  if (huruf && huruf[0] != '\0') doc["huruf"] = huruf;

  String body;
  serializeJson(doc, body);

  int kode = http.POST(body);
  if (kode > 0) {
    Serial.printf("[POST] %s -> HTTP %d | balasan: %s\n", body.c_str(), kode, http.getString().c_str());
  } else {
    // Gagal kirim: cetak error, JANGAN crash
    Serial.printf("[POST] GAGAL kirim %s | error: %s\n", body.c_str(), http.errorToString(kode).c_str());
  }
  http.end();
}

void kirimHuruf(char c) {
  char s[2] = { c, '\0' };
  kirimKeServer("HURUF", s);
}

// =============================== SENSOR ====================================
// Baca 1 sensor -> persen 0..100 (0 = lurus, 100 = tekuk penuh).
// analogRead ESP32 menghasilkan 0..4095. Rata-rata beberapa sampel utk kurangi noise.
// CATATAN: bila ternyata terbalik (lurus malah 100), ganti map jadi (100 - hasil).
int bacaPersen(int pin) {
  long total = 0;
  const int N = 5;
  for (int i = 0; i < N; i++) total += analogRead(pin);
  int mentah = total / N;
  int persen = map(mentah, 0, 4095, 0, 100);
  if (persen < 0) persen = 0;
  if (persen > 100) persen = 100;
  return persen;
}

// Kenali huruf terdekat dari kamus. Mengisi 'jarakKeluar' (Euclidean).
// Mengembalikan karakter huruf terdekat, atau 0 bila kamus kosong.
char hurufTerdekat(const int persen[5], float &jarakKeluar) {
  char terbaik = 0;
  float jarakTerbaik = 1e9;
  for (int h = 0; h < JUM_HURUF; h++) {
    long sumSq = 0;
    for (int j = 0; j < 5; j++) {
      long d = (long)persen[j] - kamus[h].pola[j];
      sumSq += d * d;               // selisih kuadrat tiap jari
    }
    float jarak = sqrt((float)sumSq); // jarak Euclidean (satuan persen)
    if (jarak < jarakTerbaik) {
      jarakTerbaik = jarak;
      terbaik = kamus[h].ch;
    }
  }
  jarakKeluar = jarakTerbaik;
  return terbaik;
}

// =============================== TOMBOL ====================================
// Debounce sederhana per tombol. Mengembalikan kondisi STABIL (true = ditekan).
bool tombolDitekan(int pin, bool &stabilState, bool &rawTerakhir, unsigned long &waktuUbah) {
  bool raw = (digitalRead(pin) == LOW); // ditekan = LOW (pullup)
  if (raw != rawTerakhir) {
    waktuUbah = millis();
    rawTerakhir = raw;
  }
  if (millis() - waktuUbah > DEBOUNCE_TOMBOL_MS) {
    stabilState = raw;
  }
  return stabilState;
}

// Variabel debounce per tombol
bool spasiStabil = false, spasiRaw = false; unsigned long spasiUbah = 0;
bool kirimStabil = false, kirimRaw = false; unsigned long kirimUbah = 0;
bool kirimSebelumnya = false;

void prosesTombol() {
  // --- SPASI: tap = SPASI, tahan >1dtk = HAPUS ---
  bool spasi = tombolDitekan(PIN_SPASI, spasiStabil, spasiRaw, spasiUbah);
  if (spasi && !spasiSedangDitekan) {
    // baru ditekan
    spasiSedangDitekan = true;
    spasiHoldTerkirim  = false;
    spasiMulai = millis();
  } else if (spasi && spasiSedangDitekan) {
    // masih ditahan -> cek apakah sudah lewat ambang HAPUS
    if (!spasiHoldTerkirim && millis() - spasiMulai > TAHAN_HAPUS_MS) {
      Serial.println("[TOMBOL] Tahan SPASI -> HAPUS");
      kirimKeServer("HAPUS", "");
      spasiHoldTerkirim = true; // kirim sekali saja
    }
  } else if (!spasi && spasiSedangDitekan) {
    // dilepas: bila belum jadi HAPUS, anggap tap = SPASI
    if (!spasiHoldTerkirim) {
      Serial.println("[TOMBOL] Tap SPASI -> SPASI");
      kirimKeServer("SPASI", "");
    }
    spasiSedangDitekan = false;
  }

  // --- KIRIM: tekan = KIRIM (pada sisi turun/awal tekan) ---
  bool kirim = tombolDitekan(PIN_KIRIM, kirimStabil, kirimRaw, kirimUbah);
  if (kirim && !kirimSebelumnya) {
    Serial.println("[TOMBOL] KIRIM -> minta Claude rapikan kalimat");
    kirimKeServer("KIRIM", "");
  }
  kirimSebelumnya = kirim;
}

// =============================== SETUP / LOOP ==============================
void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println("\n=== SIBI-Bridge Glove starting ===");

  // Pin tombol
  pinMode(PIN_SPASI, INPUT_PULLUP);
  pinMode(PIN_KIRIM, INPUT_PULLUP);
  // Pin sensor input-only (34/35/36/32/33) tidak perlu pinMode khusus untuk analogRead.

  analogReadResolution(12); // 0..4095

  hubungkanWiFi();

  if (JUM_HURUF == 0) {
    Serial.println("[KAMUS] KOSONG! Isi kamus huruf dari calibration/kalibrasi.md dulu.");
  } else {
    Serial.printf("[KAMUS] %d huruf dimuat (PLACEHOLDER bila belum dikalibrasi).\n", JUM_HURUF);
  }
}

void loop() {
  jagaWiFi();
  prosesTombol();

  // --- Baca 5 sensor jadi persen ---
  int persen[5];
  for (int j = 0; j < 5; j++) persen[j] = bacaPersen(PIN_SENSOR[j]);

  // --- Cari huruf terdekat ---
  float jarak;
  char kandidat = hurufTerdekat(persen, jarak);

  // Hanya valid bila cukup dekat (< AMBANG). Bila tidak, anggap "tangan rileks/tidak jelas".
  char valid = (kandidat != 0 && jarak < AMBANG) ? kandidat : 0;

  // --- Debounce stabilitas huruf (harus sama >= STABIL_MS) ---
  if (valid != kandidatTerakhir) {
    kandidatTerakhir = valid;
    mulaiStabil = millis();
  }

  if (valid == 0) {
    // Tangan rileks / tak ada huruf -> izinkan huruf yang sama dikirim lagi nanti
    hurufTerkirim = 0;
  } else if (valid != hurufTerkirim && (millis() - mulaiStabil >= STABIL_MS)) {
    // Huruf baru, stabil cukup lama, dan belum dikirim untuk tahanan ini
    Serial.printf("[HURUF] Terdeteksi: %c (jarak=%.1f) | sensor=[%d,%d,%d,%d,%d]\n",
                  valid, jarak, persen[0], persen[1], persen[2], persen[3], persen[4]);
    kirimHuruf(valid);
    hurufTerkirim = valid;
  }

  delay(20); // ~50 Hz; cukup untuk debounce & hemat CPU
}
