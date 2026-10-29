"""Barrido SIN llamadas a la API: con las respuestas ya guardadas por probar_vlm.py
(outputs/<video>/vlm_prueba.json) prueba distintas reglas de votación.
Uso (desde la raíz del proyecto):
  python scripts/barrido_vlm.py
Cambia PELIS si tus anotaciones están en otros archivos.
"""
import csv
import json
from collections import Counter
from pathlib import Path

PELIS = {
    "Detour": "data/annotations/anotaciones.csv",
    "TheGeneral": "outputs/TheGeneral/plantilla_300-480.csv",
}
ND = "no_determinado"


def votar(labels, umbral, min_votos):
    c = Counter(l for l in labels if l in ("mujer", "hombre"))
    n = sum(c.values())
    if n < min_votos:
        return ND
    top, k = c.most_common(1)[0]
    return top if k / n >= umbral else ND


def cargar(video, ruta_anot):
    real = {int(r["track_id"]): r["genero_percibido"].strip()
            for r in csv.DictReader(open(ruta_anot, encoding="utf-8"))
            if r["video_id"] == video and r["genero_percibido"].strip() in ("mujer", "hombre")}
    resp = json.load(open(Path("outputs") / video / "vlm_prueba.json", encoding="utf-8"))["respuestas"]
    return real, {int(k): v for k, v in resp.items()}


def main():
    datos = {v: cargar(v, a) for v, a in PELIS.items()}
    total_m = sum(1 for real, _ in datos.values() for g in real.values() if g == "mujer")
    total = sum(len(real) for real, _ in datos.values())
    print(f"{total} personas anotadas ({total_m} mujeres)\n")
    print("min_votos umbral | aciertan se_equivocan en_blanco | mujeres_reconocidas | precision_de_'mujer'")
    for mv in (1, 2, 3, 4):
        for th in (0.5, 0.6, 0.75, 0.9, 1.0):
            ok = bad = nd = mujer_ok = mujer_pred = 0
            for real, resp in datos.values():
                for tid, g in real.items():
                    p = votar(resp.get(tid, []), th, mv)
                    if p == ND:
                        nd += 1
                    elif p == g:
                        ok += 1
                    else:
                        bad += 1
                    if p == "mujer":
                        mujer_pred += 1
                        mujer_ok += (g == "mujer")
            mujeres_bien = sum(1 for real, resp in datos.values() for tid, g in real.items()
                               if g == "mujer" and votar(resp.get(tid, []), th, mv) == "mujer")
            prec = f"{mujer_ok}/{mujer_pred}" if mujer_pred else "-"
            print(f"{mv:>9} {th:>6} | {ok:>8} {bad:>12} {nd:>9} | {mujeres_bien:>2} de {total_m} | {prec}")


if __name__ == "__main__":
    main()
