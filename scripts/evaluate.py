"""Evalúa el género percibido por el sistema contra las anotaciones manuales.

Uso:
  python scripts/evaluate.py --annotations data/annotations/anotaciones.csv

El CSV de anotaciones tiene: video_id, track_id, genero_percibido, protagonista, notas
(ver data/annotations/README.md). Se compara con outputs/<video_id>/personas.json
(la predicción automática, NO la revisada).

Muestra matriz de confusión y precisión / recall / F1 por clase.


import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["mujer", "hombre", "no_determinado"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotations", default=str(ROOT / "data/annotations/anotaciones.csv"))
    ap.add_argument("--outputs", default=str(ROOT / "outputs"))
    args = ap.parse_args()

    pairs = []
    with open(args.annotations, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pfile = Path(args.outputs) / r["video_id"] / "personas.json"
            if not pfile.exists():
                continue
            pred = {p["track_id"]: p["label"]
                    for p in json.load(open(pfile, encoding="utf-8"))["personas"]}
            tid = int(r["track_id"])
            if tid in pred:
                pairs.append((r["genero_percibido"].strip(), pred[tid]))

    if not pairs:
        print("No hay pares anotación/predicción. ¿Has procesado los vídeos anotados?")
        return

    cm = Counter(pairs)
    print("Matriz de confusión (filas = anotación, columnas = predicción)")
    print("".ljust(16) + "".join(c.ljust(16) for c in CLASSES))
    for real in CLASSES:
        print(real.ljust(16) + "".join(str(cm[(real, p)]).ljust(16) for p in CLASSES))

    print("\nPor clase:")
    for c in ("mujer", "hombre"):
        tp = cm[(c, c)]
        fp = sum(cm[(r, c)] for r in CLASSES if r != c)
        fn = sum(cm[(c, p)] for p in CLASSES if p != c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        print(f"  {c:8s} precisión={prec:.2f}  recall={rec:.2f}  F1={f1:.2f}")

    undetermined = sum(1 for _, p in pairs if p == "no_determinado") / len(pairs)
    print(f"\nPersonas que el sistema deja como 'no_determinado': {100 * undetermined:.1f} %")
    print(f"Total evaluado: {len(pairs)} personas")


if __name__ == "__main__":
    main()
