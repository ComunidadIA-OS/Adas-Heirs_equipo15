"""Añade filas de plantillas rellenas a data/annotations/anotaciones.csv.

Uso (desde la raíz del proyecto):
  python scripts/anadir_anotaciones.py plantilla1.csv plantilla2.csv

- Si una persona (video_id + track_id) ya está en anotaciones.csv, no se duplica.
- Se salta las filas con el género vacío.
- Antes de modificar, guarda una copia: anotaciones.csv.bak
"""
import csv
import shutil
import sys
from pathlib import Path

DEST = Path("data/annotations/anotaciones.csv")
CAMPOS = ["video_id", "track_id", "genero_percibido", "protagonista", "notas"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(DEST, encoding="utf-8", newline="") as f:
        texto = f.read()
        f.seek(0)
        existentes = {(r["video_id"], r["track_id"]) for r in csv.DictReader(f)}
    nuevas, repes, vacias = [], 0, 0
    for ruta in sys.argv[1:]:
        with open(ruta, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if not (r.get("genero_percibido") or "").strip():
                    vacias += 1
                elif (r["video_id"], r["track_id"]) in existentes:
                    repes += 1
                else:
                    existentes.add((r["video_id"], r["track_id"]))
                    nuevas.append({k: r.get(k, "") for k in CAMPOS})
    shutil.copy(DEST, str(DEST) + ".bak")
    with open(DEST, "a", encoding="utf-8", newline="") as f:
        if texto and not texto.endswith("\n"):
            f.write("\n")
        csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n").writerows(nuevas)
    print(f"Añadidas {len(nuevas)} filas. Ya estaban: {repes}. Sin anotar (saltadas): {vacias}.")


if __name__ == "__main__":
    main()