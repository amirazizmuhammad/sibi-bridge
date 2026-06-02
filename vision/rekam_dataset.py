"""
SIBI-Bridge — Rekam Dataset Huruf (untuk melatih model akurat)
--------------------------------------------------------------
Buka kamera. Tekan tombol huruf (A-Z) sambil memperagakan bentuk tangan huruf itu;
program merekam ~1.5 detik sampel landmark untuk huruf tsb ke dataset.csv.
Ulangi tiap huruf beberapa kali dari sudut/posisi sedikit beda agar model kuat.

Target: minimal ~50-100 sampel per huruf. Tekan Q untuk selesai (otomatis tersimpan).

Setelah cukup -> jalankan: latih_model.py  (membuat model_sibi.joblib)

Privasi: hanya menyimpan ANGKA landmark (bukan gambar). dataset.csv aman.
"""
import csv
import os
import time
import sys

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import RunningMode

import sibi_common as sc

DURASI_REKAM = 1.5  # detik per tekan tombol


def hitung_label_ada():
    counts = {}
    if os.path.exists(sc.DATASET_CSV):
        with open(sc.DATASET_CSV, newline="") as f:
            r = csv.reader(f)
            header = next(r, None)
            for row in r:
                if row:
                    counts[row[0]] = counts.get(row[0], 0) + 1
    return counts


def main():
    cam = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    counts = hitung_label_ada()
    baru = not os.path.exists(sc.DATASET_CSV)
    f = open(sc.DATASET_CSV, "a", newline="")
    try:
        writer = csv.writer(f)
        if baru:
            writer.writerow(["label"] + ["f%d" % i for i in range(63)])
    except Exception:
        f.close()
        raise

    landmarker = sc.buat_landmarker(RunningMode.VIDEO)
    cap = cv2.VideoCapture(cam, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] kamera tidak terbuka"); return 1

    armed = None
    armed_until = 0.0
    print("[info] Tekan huruf A-Z untuk merekam. Q = selesai & simpan.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ts_ms = int(time.time() * 1000)
        res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts_ms)

        ada_tangan = bool(res.hand_landmarks)
        xyz = sc.xyz_dari_hasil(res.hand_landmarks[0]) if ada_tangan else None

        if xyz is not None:
            pts = [(int(x * w), int(y * h)) for x, y, _ in xyz]
            for a, b in sc.HAND_CONNECTIONS:
                cv2.line(frame, pts[a], pts[b], (0, 200, 255), 2)

        now = time.time()
        merekam = armed is not None and now < armed_until
        if merekam and xyz is not None:
            writer.writerow([armed] + ["%.5f" % v for v in sc.fitur_ternormalisasi(xyz)])
            counts[armed] = counts.get(armed, 0) + 1

        # Overlay
        cv2.rectangle(frame, (0, 0), (w, 90), (20, 20, 20), -1)
        cv2.putText(frame, "REKAM DATASET — tekan A-Z, Q=selesai", (12, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 200, 255), 2, cv2.LINE_AA)
        if merekam:
            sisa = armed_until - now
            cv2.putText(frame, "MEREKAM '%s' ... %.1fs  (total %d)" % (armed, sisa, counts.get(armed, 0)),
                        (12, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            ringkas = " ".join("%s:%d" % (k, counts[k]) for k in sorted(counts))
            cv2.putText(frame, "Sampel -> " + (ringkas or "(kosong)"), (12, 68),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 1, cv2.LINE_AA)
        if not ada_tangan:
            cv2.putText(frame, "tangan tak terdeteksi", (12, h - 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow("SIBI-Bridge — Rekam Dataset", frame)
        k = cv2.waitKey(1) & 0xFF
        if k in (ord('q'), 27):
            break
        elif 97 <= k <= 122:  # a-z
            armed = chr(k).upper()
            armed_until = now + DURASI_REKAM

    f.close()
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    print("[selesai] tersimpan ke", sc.DATASET_CSV)
    print("[ringkas]", {lbl: counts[lbl] for lbl in sorted(counts)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
