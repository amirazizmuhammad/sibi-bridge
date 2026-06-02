"""
SIBI-Bridge — Pustaka bersama untuk detektor huruf berbasis kamera.
-------------------------------------------------------------------
Dipakai oleh: sibi_camera.py (deteksi langsung), rekam_dataset.py (kumpul data),
latih_model.py (latih classifier).

Memakai MediaPipe Tasks API (HandLandmarker) — versi mediapipe 0.10.x sudah
TIDAK punya legacy `mp.solutions.hands`, jadi pakai `tasks` + file model .task.

Komentar Bahasa Indonesia. Tanpa menyimpan gambar/biometrik (privasi).
"""
import os
import numpy as np
import requests

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

# ============================ KONFIGURASI (UBAH BILA PERLU) ============================
# URL webhook n8n (sama dengan yang dipakai firmware & dashboard).
N8N_BASE    = os.environ.get("N8N_BASE", "https://n8n-kks2xqcv5bbm.jkt5.sumopod.my.id")
URL_HURUF   = N8N_BASE + "/webhook/huruf"
URL_STATUS  = N8N_BASE + "/webhook/status"
DEVICE      = "camera-01"   # identitas sumber (kontrak data sama: device/aksi/huruf)

# Token keamanan — isi env var SIBI_TOKEN atau ubah langsung di sini.
# Harus sama persis dengan konstanta SIBI_SECRET di n8n (Proses Huruf) dan SIBI_TOKEN di firmware.
# Kosong = tidak mengirim header (endpoint tidak terlindungi — cocok hanya untuk dev lokal).
SIBI_TOKEN  = os.environ.get("SIBI_TOKEN", "")

# Lokasi berkas (relatif folder vision/)
_HERE       = os.path.dirname(os.path.abspath(__file__))
MODEL_TASK  = os.path.join(_HERE, "hand_landmarker.task")  # model MediaPipe
DATASET_CSV = os.path.join(_HERE, "dataset.csv")           # hasil rekam_dataset.py
MODEL_ML    = os.path.join(_HERE, "model_sibi.joblib")     # hasil latih_model.py

# Indeks landmark tangan (21 titik MediaPipe)
WRIST = 0
TIP   = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
PIP   = {"thumb": 3, "index": 6, "middle": 10, "ring": 14, "pinky": 18}
MCP   = {"thumb": 2, "index": 5, "middle": 9,  "ring": 13, "pinky": 17}
FINGERS = ["thumb", "index", "middle", "ring", "pinky"]

# Pasangan titik untuk menggambar kerangka tangan (pengganti drawing_utils)
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),            # ibu jari
    (0,5),(5,6),(6,7),(7,8),            # telunjuk
    (9,10),(10,11),(11,12),             # tengah
    (13,14),(14,15),(15,16),            # manis
    (0,17),(17,18),(18,19),(19,20),     # kelingking
    (5,9),(9,13),(13,17),               # telapak
]

# ============================ MEDIAPIPE ============================
def buat_landmarker(mode=RunningMode.IMAGE):
    """
    Buat HandLandmarker.
    mode: RunningMode.IMAGE  → untuk foto statis / dataset_dari_foto.py
          RunningMode.VIDEO  → untuk webcam real-time (sibi_camera.py, rekam_dataset.py)
                               pakai detect_for_video(img, timestamp_ms) bukan detect(img).
    """
    if not os.path.exists(MODEL_TASK):
        raise FileNotFoundError(
            "Model tidak ditemukan: " + MODEL_TASK +
            "\nUnduh dulu: curl -L -o hand_landmarker.task "
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        )
    opts = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_TASK),
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
        running_mode=mode,
    )
    return HandLandmarker.create_from_options(opts)

def xyz_dari_hasil(hand_landmarks):
    """Ubah list 21 NormalizedLandmark jadi array (21,3) float."""
    return np.array([[p.x, p.y, p.z] for p in hand_landmarks], dtype=np.float32)

# ============================ FITUR (untuk ML) ============================
def fitur_ternormalisasi(xyz):
    """
    Normalisasi landmark agar invarian terhadap posisi & ukuran tangan:
    - geser supaya pergelangan (wrist) jadi titik (0,0,0),
    - skala dengan jarak terbesar dari wrist,
    lalu ratakan jadi vektor 63 angka (21 x 3).
    """
    p = xyz - xyz[WRIST]
    skala = np.max(np.linalg.norm(p, axis=1))
    if skala < 1e-6:
        skala = 1.0
    p = p / skala
    return p.flatten()

# ============================ HEURISTIK (mode cepat tanpa latih) ============================
def _jarak(a, b):
    return float(np.linalg.norm(a - b))

def status_jari(xyz):
    """
    Tentukan tiap jari 'terbuka' (lurus) atau 'menekuk'.
    Jari (telunjuk..kelingking): terbuka bila ujung lebih jauh dari wrist daripada PIP.
    Ibu jari: terbuka bila ujung menjauh dari pangkal telunjuk (abduksi).
    Mengembalikan dict {nama: bool terbuka} + info renggang telunjuk-tengah.
    """
    out = {}
    for f in ["index", "middle", "ring", "pinky"]:
        out[f] = _jarak(xyz[TIP[f]], xyz[WRIST]) > _jarak(xyz[PIP[f]], xyz[WRIST]) * 1.05
    # ibu jari: bandingkan jarak ujung vs IP terhadap pangkal telunjuk (MCP index)
    out["thumb"] = _jarak(xyz[TIP["thumb"]], xyz[MCP["index"]]) > _jarak(xyz[PIP["thumb"]], xyz[MCP["index"]]) * 1.05
    # renggang telunjuk-tengah (untuk bedakan U vs V)
    lebar = _jarak(xyz[TIP["index"]], xyz[TIP["middle"]])
    ukuran = _jarak(xyz[WRIST], xyz[MCP["middle"]]) + 1e-6
    out["_renggang"] = (lebar / ukuran) > 0.6
    return out

def klasifikasi_heuristik(xyz):
    """
    Tebak huruf dari pola jari terbuka/menekuk.
    Heuristik TERBATAS — hanya huruf yang pola jarinya cukup unik bisa dibedakan.
    Huruf dengan penampilan mirip (C/O/S/E/M/N/T bertumpuk di pola kepalan) butuh
    model ML untuk dibedakan.  Gunakan rekam_dataset.py + latih_model.py untuk akurasi penuh.
    Mengembalikan (huruf|None, keyakinan 0..1).

    Tabel pola (i=telunjuk, m=tengah, r=manis, p=kelingking, t=ibu jari):
      kepalan (False,False,False,False) → A  (S/E/M/N/T/O mirip — ML saja bisa bedakan)
      (True,False,False,False)          → L (t=buka) | D (t=tutup)
      (True,True,False,False)           → V (renggang) | U (rapat)
      (True,True,True,False)            → W
      (True,True,True,True)             → B  (t tutup); semua buka → open-5 (bukan SIBI baku)
      (False,False,False,True)          → Y (t=buka) | I (t=tutup)
      (False,True,True,True)            → F  (telunjuk melekuk sentuh ibu jari, 3 jari lain buka)
      (True,False,True,True)            → bukan SIBI baku, skip
      (False,True,False,False)          → bukan SIBI baku, skip
    """
    s = status_jari(xyz)
    t, i, m, r, p = s["thumb"], s["index"], s["middle"], s["ring"], s["pinky"]
    pola = (i, m, r, p)  # 4 jari utama

    if pola == (False, False, False, False):
        # kepalan: A/S/T/E/M/N/O semua mirip → ambil A (paling umum di awal kata)
        # conf 0.60 (tepat di ambang default --min-conf 0.6) supaya lolos filter
        return ("A", 0.60)
    if pola == (True, False, False, False):
        return ("L", 0.6) if t else ("D", 0.6)
    if pola == (True, True, False, False):
        return ("V", 0.65) if s["_renggang"] else ("U", 0.65)
    if pola == (True, True, True, False):
        return ("W", 0.7)
    if pola == (True, True, True, True):
        # B = 4 jari tegak, ibu jari dilipat di dalam
        return ("B", 0.7)
    if pola == (False, False, False, True):
        return ("Y", 0.6) if t else ("I", 0.65)
    if pola == (False, True, True, True):
        # F = telunjuk melekuk menyentuh ibu jari, tengah/manis/kelingking tegak
        return ("F", 0.60)
    # pola lain membutuhkan model ML (C, G, H, J, K, M, N, O, P, Q, R, S, T, X, Z)
    return (None, 0.0)

# ============================ KOMUNIKASI n8n ============================
_sesi = requests.Session()

def kirim_aksi(aksi, huruf=None, timeout=6):
    """POST ke /webhook/huruf. Mengembalikan (ok: bool, data|pesan)."""
    body = {"device": DEVICE, "aksi": aksi}
    if huruf:
        body["huruf"] = huruf
    headers = {}
    if SIBI_TOKEN:
        headers["X-SIBI-Token"] = SIBI_TOKEN
    try:
        r = _sesi.post(URL_HURUF, json=body, headers=headers, timeout=timeout)
        if r.status_code >= 400:
            return (False, "HTTP %d: %s" % (r.status_code, r.text[:200]))
        try:
            return (True, r.json())
        except Exception:
            return (True, r.text)
    except Exception as e:
        return (False, str(e))

def baca_status(timeout=4):
    """GET /webhook/status. Mengembalikan dict atau None bila gagal."""
    try:
        r = _sesi.get(URL_STATUS, timeout=timeout)
        if r.status_code >= 400:
            return None
        return r.json()
    except Exception:
        return None
