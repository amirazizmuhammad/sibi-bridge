"""
SIBI-Bridge — Buat Dataset dari FOTO (bukan webcam)
---------------------------------------------------
Baca folder berisi foto huruf SIBI, jalankan MediaPipe HandLandmarker tiap foto,
ekstrak 21 titik tangan -> tulis ke dataset.csv (format sama dgn rekam_dataset.py).
Lalu jalankan latih_model.py untuk membuat model_sibi.joblib.

CARA LABEL (pilih salah satu):
  A) Subfolder per huruf (DISARANKAN, paling aman):
       vision/foto/A/ ... (isi foto huruf A)
       vision/foto/B/ ...
  B) Nama file diawali huruf:  A.jpg, A_1.jpg, B-2.png  -> label dari huruf pertama nama.

Jalankan:
  .venv\\Scripts\\python.exe dataset_dari_foto.py            # baca folder vision/foto
  .venv\\Scripts\\python.exe dataset_dari_foto.py D:\\fotoku  # folder lain

SYARAT FOTO: tangan ASLI (bukan ilustrasi/kartun), 1 tangan/foto, jelas & terang.
Privasi: hanya angka landmark yang disimpan, bukan foto.
"""
import csv
import os
import re
import sys

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

import sibi_common as sc

EKSTENSI = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def baca_gambar(path):
    """imdecode agar tahan path non-ASCII / spasi."""
    try:
        data = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def kumpulkan_foto(root):
    """Kembalikan list (path, label)."""
    pasangan = []
    subdirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    if subdirs:
        # Mode A: subfolder = label
        for d in subdirs:
            label = d.strip().upper()
            for nm in os.listdir(os.path.join(root, d)):
                if nm.lower().endswith(EKSTENSI):
                    pasangan.append((os.path.join(root, d, nm), label))
    else:
        # Mode B: huruf pertama nama file
        for nm in os.listdir(root):
            if nm.lower().endswith(EKSTENSI):
                m = re.search(r"[A-Za-z]", nm)
                if m:
                    pasangan.append((os.path.join(root, nm), m.group().upper()))
    return pasangan


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(sc._HERE, "foto")
    if not os.path.isdir(root):
        print("[ERROR] folder tidak ada:", root)
        print("Buat folder 'vision/foto' lalu isi subfolder per huruf (foto/A, foto/B, ...).")
        return 1

    pasangan = kumpulkan_foto(root)
    if not pasangan:
        print("[ERROR] tidak ada foto (.jpg/.png/...) di", root)
        return 1
    print("[info] %d foto ditemukan di %s" % (len(pasangan), root))

    # Landmarker mode IMAGE (boleh 2 tangan, ambil yang pertama)
    opts = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=sc.MODEL_TASK),
        num_hands=1, min_hand_detection_confidence=0.5, running_mode=RunningMode.IMAGE,
    )
    lm = HandLandmarker.create_from_options(opts)

    baru = not os.path.exists(sc.DATASET_CSV)
    f = open(sc.DATASET_CSV, "a", newline="")
    ok_count, gagal = {}, []
    try:
        w = csv.writer(f)
        if baru:
            w.writerow(["label"] + ["f%d" % i for i in range(63)])

        for path, label in pasangan:
            img = baca_gambar(path)
            if img is None:
                gagal.append((path, "tak bisa dibaca")); continue
            rgb = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
            if not res.hand_landmarks:
                gagal.append((path, "tangan tak terdeteksi")); continue
            xyz = sc.xyz_dari_hasil(res.hand_landmarks[0])
            w.writerow([label] + ["%.5f" % v for v in sc.fitur_ternormalisasi(xyz)])
            ok_count[label] = ok_count.get(label, 0) + 1
    finally:
        f.close()
        lm.close()

    total_ok = sum(ok_count.values())
    print("\n[selesai] %d foto sukses jadi sampel -> %s" % (total_ok, sc.DATASET_CSV))
    for l in sorted(ok_count):
        print("   %s : %d" % (l, ok_count[l]))
    if gagal:
        print("\n[%d foto GAGAL] (tangan tak terdeteksi / ilustrasi / buram):" % len(gagal))
        for p, alasan in gagal[:20]:
            print("   -", os.path.basename(p), "->", alasan)
        if len(gagal) > 20:
            print("   ... dan %d lagi" % (len(gagal) - 20))
    print("\nLangkah berikutnya: jalankan LATIH-MODEL.bat (atau latih_model.py).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
