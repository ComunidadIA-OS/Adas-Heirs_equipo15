"""Etapa 6 — Métricas de presencia y protagonismo.

Por persona (trayectoria):
  screen_time_s   tiempo en pantalla (observaciones / fps_sample)
  size            área media de la caja respecto al frame (0–1)
  centrality      1 = centro exacto del frame, 0 = esquina
  solo            fracción de sus frames en los que es la única persona visible
  edges           1 si aparece al principio o al final del vídeo (edge_fraction), si no 0
  n_shots         número de planos en los que aparece
  protagonism     índice ponderado (pesos en config.yaml), 0–1

Por género percibido: % de tiempo en pantalla, % de personas, índice medio, % de protagonistas.

Salida: metricas.json  {"personas": [...], "por_genero": {...}, "resumen": {...}}
Si existe personas_revisado.json (corregido por una persona en la demo), se usa ese en lugar
de personas.json: la revisión humana tiene prioridad.
"""

import math
from collections import defaultdict

from .utils import load_json, save_json


def person_features(observations, width, height, fps_sample, duration_s,
                    frames_with_count, edge_fraction=0.1):
    """observations: observaciones de UNA trayectoria. frames_with_count: {frame: nº personas}."""
    cx0, cy0 = width / 2, height / 2
    max_dist = math.hypot(cx0, cy0)
    sizes, cents, solos = [], [], []
    for o in observations:
        x1, y1, x2, y2 = o["box"]
        sizes.append(max(0.0, (x2 - x1) * (y2 - y1)) / (width * height))
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        cents.append(1 - math.hypot(cx - cx0, cy - cy0) / max_dist)
        solos.append(1.0 if frames_with_count.get(o["frame"], 0) == 1 else 0.0)

    times = [o["t"] for o in observations]
    edge_s = edge_fraction * duration_s
    at_edges = any(t <= edge_s for t in times) or any(t >= duration_s - edge_s for t in times)
    n = len(observations)
    return {
        "screen_time_s": n / fps_sample,
        "size": sum(sizes) / n,
        "centrality": sum(cents) / n,
        "solo": sum(solos) / n,
        "edges": 1.0 if at_edges else 0.0,
        "n_shots": len({o["shot_id"] for o in observations}),
        "first_t": min(times),
    }


def protagonism_index(features, max_screen_time, max_size, weights):
    """Normaliza cada componente a 0–1 y hace la media ponderada."""
    comps = {
        "screen_time": features["screen_time_s"] / max_screen_time if max_screen_time else 0.0,
        "size": features["size"] / max_size if max_size else 0.0,
        "centrality": features["centrality"],
        "solo": features["solo"],
        "edges": features["edges"],
    }
    total_w = sum(weights.values())
    return sum(comps[k] * w for k, w in weights.items()) / total_w


def compute(tracks, personas, mcfg):
    obs_by_track = defaultdict(list)
    frames_with_count = defaultdict(int)
    for o in tracks["observations"]:
        obs_by_track[o["track_id"]].append(o)
        frames_with_count[o["frame"]] += 1

    labels = {p["track_id"]: p["label"] for p in personas}
    feats = {}
    for tid, obs in obs_by_track.items():
        feats[tid] = person_features(obs, tracks["width"], tracks["height"], tracks["fps_sample"],
                                     tracks["duration_s"], frames_with_count, mcfg["edge_fraction"])

    max_st = max((f["screen_time_s"] for f in feats.values()), default=0)
    max_sz = max((f["size"] for f in feats.values()), default=0)
    rows = []
    for tid, f in feats.items():
        idx = protagonism_index(f, max_st, max_sz, mcfg["weights"])
        rows.append({"track_id": tid, "label": labels.get(tid, "no_determinado"),
                     **{k: round(v, 4) if isinstance(v, float) else v for k, v in f.items()},
                     "protagonism": round(idx, 4),
                     "protagonist": idx >= mcfg["protagonist_threshold"]})
    rows.sort(key=lambda r: r["protagonism"], reverse=True)

    total_time = sum(r["screen_time_s"] for r in rows) or 1.0
    groups = defaultdict(list)
    for r in rows:
        groups[r["label"]].append(r)
    por_genero = {}
    for label, rs in groups.items():
        por_genero[label] = {
            "personas": len(rs),
            "pct_personas": round(100 * len(rs) / len(rows), 1),
            "screen_time_s": round(sum(r["screen_time_s"] for r in rs), 1),
            "pct_screen_time": round(100 * sum(r["screen_time_s"] for r in rs) / total_time, 1),
            "protagonism_medio": round(sum(r["protagonism"] for r in rs) / len(rs), 3),
            "protagonistas": sum(r["protagonist"] for r in rs),
        }
    n_prot = sum(r["protagonist"] for r in rows) or 1
    for label, g in por_genero.items():
        g["pct_protagonistas"] = round(100 * g["protagonistas"] / n_prot, 1)

    resumen = {"duration_s": tracks["duration_s"], "personas": len(rows),
               "persona_mas_protagonista": rows[0]["track_id"] if rows else None}
    return {"personas": rows, "por_genero": por_genero, "resumen": resumen}


def run(video_path, cfg, outdir):
    tracks = load_json(outdir / "tracks.json")
    revised = outdir / "personas_revisado.json"
    personas_file = revised if revised.exists() else outdir / "personas.json"
    personas = load_json(personas_file)["personas"]
    result = compute(tracks, personas, cfg["metrics"])
    result["fuente_etiquetas"] = personas_file.name
    save_json(result, outdir / "metricas.json")
    print(f"[metrics] {result['por_genero']}")
    return result
