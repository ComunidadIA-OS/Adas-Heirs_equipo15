"""Junta las métricas de todas las películas procesadas y las resume por década.

Uso:  python scripts/resumen_corpus.py
Salida: outputs/resumen_corpus.csv (una fila por película) y una tabla por década en pantalla.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def main():
    with open(ROOT / "data" / "sources.csv", encoding="utf-8") as f:
        films = {r["id"]: r for r in csv.DictReader(f)}

    rows = []
    for fid, film in films.items():
        mfile = OUT / fid / "metricas.json"
        if not mfile.exists():
            continue
        m = json.load(open(mfile, encoding="utf-8"))
        pg = m["por_genero"]
        t_m = pg.get("mujer", {}).get("screen_time_s", 0.0)
        t_h = pg.get("hombre", {}).get("screen_time_s", 0.0)
        rows.append({
            "id": fid, "titulo": film["titulo"], "anio": film["anio"], "decada": film["decada"],
            "pct_tiempo_mujeres": pg.get("mujer", {}).get("pct_screen_time", 0.0),
            "pct_personas_mujeres": pg.get("mujer", {}).get("pct_personas", 0.0),
            "pct_protagonistas_mujeres": pg.get("mujer", {}).get("pct_protagonistas", 0.0),
            "pct_no_determinado": pg.get("no_determinado", {}).get("pct_personas", 0.0),
            "pct_tiempo_no_determinado": pg.get("no_determinado", {}).get("pct_screen_time", 0.0),
            # % de mujeres SOLO entre el tiempo con género determinado (mujer + hombre):
            # no depende de cuántas personas quedan como no_determinado
            "pct_tiempo_mujeres_determinado": round(100 * t_m / (t_m + t_h), 1) if t_m + t_h else 0.0,
            "fuente_etiquetas": m.get("fuente_etiquetas", ""),
        })

    if not rows:
        print("No hay películas procesadas todavía.")
        return

    with open(OUT / "resumen_corpus.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    by_dec = defaultdict(list)
    for r in rows:
        by_dec[r["decada"]].append(r)
    print(f"{'Década':8s} {'Películas':>9s} {'% tiempo mujeres':>17s} {'% mujeres (determ.)':>20s} "
          f"{'% tiempo no_det.':>17s} {'% protagonistas':>16s}")
    for dec in sorted(by_dec):
        rs = by_dec[dec]
        t = sum(r["pct_tiempo_mujeres"] for r in rs) / len(rs)
        d = sum(r["pct_tiempo_mujeres_determinado"] for r in rs) / len(rs)
        u = sum(r["pct_tiempo_no_determinado"] for r in rs) / len(rs)
        p = sum(r["pct_protagonistas_mujeres"] for r in rs) / len(rs)
        print(f"{dec:8s} {len(rs):9d} {t:16.1f}% {d:19.1f}% {u:16.1f}% {p:15.1f}%")
    print("\n'% mujeres (determ.)' = tiempo de mujeres / (tiempo de mujeres + hombres), sin contar no_determinado.")
    print(f"\nDetalle por película en {OUT / 'resumen_corpus.csv'}")
    print("Ojo: pocas películas por década -> tendencias exploratorias, no conclusiones generales.")


if __name__ == "__main__":
    main()
