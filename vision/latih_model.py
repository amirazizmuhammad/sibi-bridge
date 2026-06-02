"""
SIBI-Bridge — Latih Model Huruf dari dataset.csv
------------------------------------------------
Baca dataset.csv (hasil rekam_dataset.py), latih classifier (KNN), laporkan
akurasi validasi-silang, simpan ke model_sibi.joblib.

Jalankan: .venv\\Scripts\\python.exe latih_model.py
Lalu sibi_camera.py otomatis memakai model itu (lebih akurat dari heuristik).
"""
import csv
import os
import sys

import numpy as np

import sibi_common as sc


def muat_dataset():
    if not os.path.exists(sc.DATASET_CSV):
        print("[ERROR] dataset.csv belum ada. Jalankan rekam_dataset.py dulu.")
        sys.exit(1)
    X, y = [], []
    with open(sc.DATASET_CSV, newline="") as f:
        r = csv.reader(f)
        next(r, None)  # header
        for row in r:
            if len(row) == 64:
                y.append(row[0])
                X.append([float(v) for v in row[1:]])
    return np.array(X, dtype=np.float32), np.array(y)


def main():
    X, y = muat_dataset()
    labels, counts = np.unique(y, return_counts=True)
    print("[data] %d sampel, %d huruf:" % (len(y), len(labels)))
    for l, c in zip(labels, counts):
        tanda = "  <-- kurang (idealnya >=30)" if c < 30 else ""
        print("   %s : %d%s" % (l, c, tanda))

    if len(labels) < 2:
        print("[ERROR] minimal 2 huruf berbeda untuk melatih."); return 1

    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score

    n_neighbors = min(5, int(np.min(counts)))
    n_neighbors = max(1, n_neighbors)
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance"))

    # Validasi silang (bila tiap kelas cukup)
    cv = int(min(5, np.min(counts)))
    if cv >= 2:
        skor = cross_val_score(model, X, y, cv=cv)
        print("[akurasi] validasi-silang %d-fold: %.1f%% (±%.1f%%)" % (cv, skor.mean() * 100, skor.std() * 100))
    else:
        print("[akurasi] sampel terlalu sedikit untuk validasi-silang; tambah data.")

    model.fit(X, y)
    import joblib
    joblib.dump(model, sc.MODEL_ML)
    print("[selesai] model tersimpan:", sc.MODEL_ML)
    print("           Jalankan sibi_camera.py — otomatis memakai model ini.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
