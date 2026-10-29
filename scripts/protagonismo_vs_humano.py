"""Compara el protagonismo que calcula el sistema con tu anotación (columna protagonista).
Uso (desde la raíz del proyecto):
  python scripts/protagonismo_vs_humano.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

ANOT = "data/annotations/anotaciones.csv"
OUT = Path("outputs")


def main():
    rows = list(csv.DictReader(open(ANOT, encoding="utf-8")))
    cm = Counter()
    fallos = []
    for vid in sorted({r["video_id"] for r in rows}):
        f = OUT / vid / "metricas.json"
        if not f.exists():
            print(f"(sin metricas.json para {vid}, se salta)")
            continue
        m = {p["track_id"]: p for p in json.load(open(f, encoding="utf-8"))["personas"]}
        for r in rows:
            if r["video_id"] != vid:
                continue
            p = m.get(int(r["track_id"]))
            if p is None or r["protagonista"].strip() not in ("si", "no"):
                continue
            real = r["protagonista"].strip()
            pred = "si" if p["protagonist"] else "no"
            cm[(real, pred)] += 1
            if real != pred:
                fallos.append((vid, r["track_id"], real, pred, p["protagonism"]))
    print("            modelo si  modelo no")
    for real in ("si", "no"):
        print(f"tú {real:3s}      {cm[(real, 'si')]:5d}      {cm[(real, 'no')]:5d}")
    total = sum(cm.values())
    if total:
        acc = (cm[("si", "si")] + cm[("no", "no")]) / total
        print(f"\nCoinciden {cm[('si', 'si')] + cm[('no', 'no')]} de {total} ({100 * acc:.0f} %)")
    print("\nDesacuerdos (video, track, tú, modelo, índice):")
    for x in fallos:
        print(x)


if __name__ == "__main__":
    main()
