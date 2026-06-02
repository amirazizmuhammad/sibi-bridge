"""
SIBI-Bridge — Detektor Huruf via Kamera (pengganti sarung tangan)
-----------------------------------------------------------------
Webcam -> MediaPipe HandLandmarker (21 titik) -> klasifikasi huruf SIBI
-> debounce -> POST {device,aksi:'HURUF',huruf} ke webhook n8n yang SAMA.

Backend (n8n + Claude + dashboard) TIDAK berubah. Tombol SPASI/KIRIM/HAPUS
diganti tombol keyboard (belum ada tombol fisik di mode kamera).

Mode klasifikasi:
- Bila ada model terlatih (model_sibi.joblib) -> pakai itu (akurat, semua huruf yang dilatih).
- Bila belum -> heuristik bawaan (terbatas ~10 huruf jelas).
  Untuk akurasi: jalankan rekam_dataset.py lalu latih_model.py.

Jalankan:
  .venv\\Scripts\\python.exe sibi_camera.py                # mode normal (kirim ke n8n)
  .venv\\Scripts\\python.exe sibi_camera.py --no-send       # uji deteksi tanpa kirim
  .venv\\Scripts\\python.exe sibi_camera.py --selftest      # uji jalur Python->n8n tanpa kamera
  .venv\\Scripts\\python.exe sibi_camera.py --camera 1      # pilih kamera lain

Kontrol keyboard (di jendela kamera):
  SPASI = spasi | ENTER = KIRIM (Claude) | BACKSPACE = HAPUS
  A = auto-kirim ON/OFF | S = kirim huruf saat ini manual | Q/ESC = keluar
"""
import argparse
import time
import sys
import threading

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import RunningMode

import sibi_common as sc

# ============================ THREADING HTTP ============================
# Kirim ke n8n di thread terpisah agar main loop kamera tidak terblokir.
_kirim_lock = threading.Lock()
_kirim_pesan = {"v": ""}   # pesan terakhir untuk overlay

def _do_kirim(aksi, huruf):
    ok, data = sc.kirim_aksi(aksi, huruf)
    if aksi == "HURUF":
        msg = ("terkirim '%s'" % huruf) if ok else ("GAGAL: %s" % str(data)[:80])
    else:
        msg = ("%s OK" % aksi) if ok else ("GAGAL %s: %s" % (aksi, str(data)[:60]))
    with _kirim_lock:
        _kirim_pesan["v"] = msg

def kirim_nonblok(aksi, huruf=None):
    """Kirim aksi ke n8n tanpa memblokir loop kamera."""
    threading.Thread(target=_do_kirim, args=(aksi, huruf), daemon=True).start()


def muat_classifier():
    """Kembalikan fungsi prediksi (xyz)->(huruf|None, conf) + label mode."""
    import os
    if os.path.exists(sc.MODEL_ML):
        try:
            import joblib
            model = joblib.load(sc.MODEL_ML)
            def pred(xyz):
                fitur = sc.fitur_ternormalisasi(xyz).reshape(1, -1)
                huruf = model.predict(fitur)[0]
                conf = 1.0
                if hasattr(model, "predict_proba"):
                    conf = float(np.max(model.predict_proba(fitur)))
                return (str(huruf), conf)
            return pred, "MODEL ML (model_sibi.joblib)"
        except Exception as e:
            print("[peringatan] gagal muat model ML (%s) -> pakai heuristik" % e)
    return (lambda xyz: sc.klasifikasi_heuristik(xyz)), "HEURISTIK (terbatas)"


def gambar_tangan(frame, xyz):
    """Gambar kerangka tangan + titik (pengganti drawing_utils)."""
    h, w = frame.shape[:2]
    pts = [(int(x * w), int(y * h)) for x, y, _ in xyz]
    for a, b in sc.HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 200, 255), 2)
    for (x, y) in pts:
        cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)


def teks(frame, s, org, skala=0.7, warna=(255, 255, 255), tebal=2):
    cv2.putText(frame, s, org, cv2.FONT_HERSHEY_SIMPLEX, skala, (0, 0, 0), tebal + 2, cv2.LINE_AA)
    cv2.putText(frame, s, org, cv2.FONT_HERSHEY_SIMPLEX, skala, warna, tebal, cv2.LINE_AA)


def selftest():
    """Uji jalur Python -> n8n tanpa kamera (membuktikan integrasi)."""
    print("=== SELFTEST: kirim 'HALO' lalu KIRIM ke", sc.URL_HURUF)
    for ch in "HALO":
        ok, data = sc.kirim_aksi("HURUF", ch)
        print("  HURUF %s -> ok=%s data=%s" % (ch, ok, data))
    ok, data = sc.kirim_aksi("KIRIM")
    print("  KIRIM -> ok=%s" % ok)
    if ok and isinstance(data, dict):
        h = data.get("hasil") or {}
        print("  hasil.teks =", h.get("teks"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0, help="indeks kamera (default 0)")
    ap.add_argument("--no-send", action="store_true", help="jangan kirim ke n8n (uji deteksi saja)")
    ap.add_argument("--selftest", action="store_true", help="uji jalur Python->n8n tanpa kamera")
    ap.add_argument("--hold-ms", type=int, default=800, help="lama huruf harus stabil sebelum dikirim")
    ap.add_argument("--min-conf", type=float, default=0.6, help="ambang keyakinan minimum")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    pred, mode_label = muat_classifier()
    print("[info] mode klasifikasi:", mode_label)
    print("[info] kirim ke:", "(NONAKTIF, --no-send)" if args.no_send else sc.URL_HURUF)

    landmarker = sc.buat_landmarker(RunningMode.VIDEO)  # VIDEO: temporal tracking lebih stabil dari IMAGE
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)  # CAP_DSHOW: pembuka kamera cepat di Windows
    if not cap.isOpened():
        print("[ERROR] kamera %d tidak terbuka. Coba --camera 1." % args.camera)
        return 1

    auto_kirim = True
    huruf_kandidat = None
    kandidat_sejak = 0.0
    huruf_terkirim = None    # jangan kirim ulang sampai tangan berubah/rileks
    status_cache = {"buffer": "", "hasil": None}
    last_poll = 0.0
    conn_ok = False
    pesan = ""

    print("[info] tekan Q/ESC untuk keluar. SPASI/ENTER/BACKSPACE = aksi.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("[ERROR] gagal baca frame"); break
        frame = cv2.flip(frame, 1)  # cermin agar gerakan natural
        h, w = frame.shape[:2]

        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        hasil = landmarker.detect_for_video(mp_img, int(time.time() * 1000))

        huruf_now, conf = None, 0.0
        if hasil.hand_landmarks:
            xyz = sc.xyz_dari_hasil(hasil.hand_landmarks[0])
            gambar_tangan(frame, xyz)
            huruf_now, conf = pred(xyz)
            if conf < args.min_conf:
                huruf_now = None

        # ---- Debounce: huruf harus stabil >= hold-ms ----
        now = time.time()
        if huruf_now is None:
            huruf_kandidat = None
            huruf_terkirim = None   # tangan rileks -> izinkan kirim huruf sama lagi nanti
        else:
            if huruf_now != huruf_kandidat:
                huruf_kandidat = huruf_now
                kandidat_sejak = now
            elif (now - kandidat_sejak) * 1000 >= args.hold_ms and huruf_now != huruf_terkirim:
                # stabil cukup lama & belum dikirim untuk tahanan ini
                if auto_kirim and not args.no_send:
                    kirim_nonblok("HURUF", huruf_now)
                    pesan = "kirim '%s'…" % huruf_now
                else:
                    pesan = "deteksi '%s' (tak dikirim)" % huruf_now
                huruf_terkirim = huruf_now

        # ---- Polling status tiap ~1 dtk untuk tampilkan buffer/hasil ----
        if now - last_poll > 1.0 and not args.no_send:
            last_poll = now
            st = sc.baca_status()
            if st is not None:
                conn_ok = True
                status_cache["buffer"] = st.get("buffer", "")
                status_cache["hasil"] = st.get("hasil")
            else:
                conn_ok = False
        # Perbarui pesan overlay dari hasil HTTP thread
        with _kirim_lock:
            if _kirim_pesan["v"]:
                pesan = _kirim_pesan["v"]
                _kirim_pesan["v"] = ""

        # ---- Overlay ----
        bar = max(120, int(h * 0.30))
        cv2.rectangle(frame, (0, 0), (w, bar), (20, 20, 20), -1)
        teks(frame, "SIBI-Bridge Kamera  [%s]" % mode_label, (12, 28), 0.6, (120, 200, 255))
        bigwarna = (0, 255, 120) if huruf_now else (120, 120, 120)
        teks(frame, "Huruf: %s" % (huruf_now or "-"), (12, 78), 1.4, bigwarna, 3)
        if huruf_now:
            teks(frame, "conf %.0f%%" % (conf * 100), (300, 78), 0.8, bigwarna, 2)
        teks(frame, "Buffer: %s" % (status_cache["buffer"] or ""), (12, bar - 38), 0.8, (255, 255, 0))
        hasil_teks = (status_cache["hasil"] or {}).get("teks", "") if status_cache["hasil"] else ""
        teks(frame, "Kalimat: %s" % hasil_teks, (12, bar - 10), 0.8, (255, 255, 255))
        # status koneksi + auto
        ckon = (0, 255, 0) if conn_ok else (0, 0, 255)
        cv2.circle(frame, (w - 24, 22), 9, ckon, -1)
        teks(frame, "n8n" if conn_ok else "x", (w - 70, 28), 0.6, ckon, 2)
        teks(frame, "AUTO:%s" % ("ON" if auto_kirim else "OFF"), (w - 150, bar - 10), 0.6,
             (0, 255, 0) if auto_kirim else (0, 165, 255), 2)
        teks(frame, "SPASI ENTER=KIRIM BKSP=HAPUS A=auto S=kirim Q=keluar", (12, h - 14), 0.55, (200, 200, 200), 1)
        if pesan:
            teks(frame, pesan, (300, 28), 0.55, (180, 255, 180), 1)

        cv2.imshow("SIBI-Bridge — Kamera", frame)

        # ---- Keyboard ----
        k = cv2.waitKey(1) & 0xFF
        if k in (ord('q'), 27):       # Q / ESC
            break
        elif k == ord('a'):
            auto_kirim = not auto_kirim
        elif k == 32:                 # SPASI
            if not args.no_send: kirim_nonblok("SPASI"); pesan = "SPASI…"
        elif k in (13, 10):           # ENTER -> KIRIM
            if not args.no_send: kirim_nonblok("KIRIM"); pesan = "KIRIM (Claude)…"
        elif k == 8:                  # BACKSPACE -> HAPUS
            if not args.no_send: kirim_nonblok("HAPUS"); pesan = "HAPUS…"
        elif k == ord('s'):           # kirim huruf saat ini (manual)
            if huruf_now and not args.no_send:
                kirim_nonblok("HURUF", huruf_now); pesan = "kirim manual '%s'…" % huruf_now

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
