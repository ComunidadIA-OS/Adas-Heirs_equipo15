"""Explora por qué el índice de protagonismo no coincide con tu anotación.
Recalcula el índice con otras configuraciones SIN reejecutar el pipeline.
Uso (desde la raíz del proyecto):
  python scripts/protagonismo_explorar.py --video Detour
Es una exploración con pocas filas: sirve para entender, no para afinar hasta el último decimal.
"""
import argparse
import csv
import json
import math
from pathlib import Path


def load(p):
    return json.load(open(p, encoding="utf-8"))


def puntos_fuertes(w, h):
    return [(w / 2, h / 2)] + [(x, y) for x in (w / 3, 2 * w / 3) for y in (h / 3, 2 * h / 3)]


def composicion(box, w, h):
    """1 = ojos aprox. justo en el centro o en una intersección de tercios; 0 = lejos."""
    x1, y1, x2, y2 = box
    cx, cy = (x1 + x2) / 2, y1 + 0.2 * (y2 - y1)
    d = min(math.hypot(cx - px, cy - py) for px, py in puntos_fuertes(w, h))
    return max(0.0, 1 - d / (0.3 * math.hypot(w, h)))


def indice(c, pesos):
    return sum(c[k] * w for k, w in pesos.items()) / sum(pesos.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="Detour")
    ap.add_argument("--annotations", default="data/annotations/anotaciones.csv")
    args = ap.parse_args()
    out = Path("outputs") / args.video
    real = {int(r["track_id"]): r["protagonista"].strip()
            for r in csv.DictReader(open(args.annotations, encoding="utf-8"))
            if r["video_id"] == args.video and r["protagonista"].strip() in ("si", "no")}
    met = load(out / "metricas.json")["personas"]
    tracks = load(out / "tracks.json")
    W, H = tracks["width"], tracks["height"]
    max_st = max(p["screen_time_s"] for p in met) or 1
    max_sz = max(p["size"] for p in met) or 1

    obs = {}
    for o in tracks["observations"]:
        if o["track_id"] in real:
            obs.setdefault(o["track_id"], []).append(o)

    feats = {}
    for p in met:
        t = p["track_id"]
        if t not in real or t not in obs:
            continue
        ob = obs[t]
        feats[t] = {
            "st": p["screen_time_s"] / max_st, "sz": p["size"] / max_sz,
            "ce": p["centrality"], "so": p["solo"], "ed": p["edges"],
            "co": sum(composicion(o["box"], W, H) for o in ob) / len(ob),
            "cu": sum(1.0 for o in ob if (o["box"][3] - o["box"][1]) / H >= 0.5) / len(ob),
        }

    variantes = {
        "actual (con edges)": {"st": .30, "sz": .20, "ce": .15, "so": .20, "ed": .15},
        "sin edges": {"st": .30, "sz": .20, "ce": .15, "so": .20},
        "composicion + primer plano (Luna)": {"st": .20, "sz": .15, "co": .20, "so": .20, "cu": .25},
    }
    ths = [round(0.2 + 0.025 * i, 3) for i in range(0, 21)]
    print(f"{len(feats)} tracks anotados de {args.video} ({sum(v == 'si' for v in real.values())} protagonistas según tú)\n")
    print("Índice por tipo; acierto = coincide con tu si/no. Umbral 0,5 y mejor umbral posible:")
    for nombre, pesos in variantes.items():
        idx = {t: indice(f, pesos) for t, f in feats.items()}
        def acc(th):
            return sum((idx[t] >= th) == (real[t] == "si") for t in feats) / len(feats)
        mejor = max(acc(th) for th in ths)
        rango = [th for th in ths if acc(th) == mejor]
        print(f"- {nombre}: umbral 0,5 -> {100 * acc(0.5):.0f} % | "
              f"mejor {100 * mejor:.0f} % con umbral entre {min(rango)} y {max(rango)}")

    print("\nTrack  tú   screen  tamaño  centro  solo  composic  primerPl | índice actual / Luna")
    pa, pl = variantes["actual (con edges)"], variantes["composicion + primer plano (Luna)"]
    for t in sorted(feats, key=lambda x: (real[x] != "si", x)):
        f = feats[t]
        print(f"{t:>6} {real[t]:>3}  {f['st']:6.2f}  {f['sz']:6.2f}  {f['ce']:6.2f}  {f['so']:4.2f}  "
              f"{f['co']:8.2f}  {f['cu']:8.2f} | {indice(f, pa):.2f} / {indice(f, pl):.2f}")


if __name__ == "__main__":
    main()
