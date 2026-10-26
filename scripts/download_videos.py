"""Descarga los vídeos listados en data/sources.csv (solo las filas con usar = si).

Si la fila tiene 'url_descarga', se usa ese enlace. Si no, el script pregunta a la API de
Internet Archive (https://archive.org/metadata/<id>) qué ficheros tiene la película y elige
un .mp4 (preferencia: h.264 > MPEG4 > 512Kb MPEG4; el más grande por debajo de MAX_GB).

Uso:
  python scripts/download_videos.py                    # a data/videos/
  python scripts/download_videos.py --dest /workspace/videos
  python scripts/download_videos.py --solo Detour      # una sola película
"""

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.csv"
PREFERRED = ["h.264", "mpeg4", "512kb mpeg4", "h.264 ia"]
MAX_GB = 3.0
UA = {"User-Agent": "reto-mujeres-ia-abierta (investigacion academica)"}


def elegir_mp4(identifier):
    req = urllib.request.Request(f"https://archive.org/metadata/{identifier}", headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        meta = json.load(resp)
    candidatos = []
    for f in meta.get("files", []):
        name = f.get("name", "")
        fmt = f.get("format", "").lower()
        size = int(f.get("size", 0) or 0)
        if not name.lower().endswith(".mp4") or size > MAX_GB * 1024 ** 3:
            continue
        rank = PREFERRED.index(fmt) if fmt in PREFERRED else len(PREFERRED)
        candidatos.append((rank, -size, name))
    elegido = None
    if candidatos:
        candidatos.sort()
        elegido = candidatos[0][2]
    return elegido


def descargar(url, dest):
    tmp = dest.with_suffix(".part")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as out:
        total = int(resp.headers.get("Content-Length", 0) or 0)
        hecho = 0
        bloque = resp.read(1024 * 1024)
        while bloque:
            out.write(bloque)
            hecho += len(bloque)
            if total:
                print(f"\r   {hecho / 1e6:.0f} / {total / 1e6:.0f} MB", end="", flush=True)
            bloque = resp.read(1024 * 1024)
    print()
    tmp.rename(dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=str(ROOT / "data" / "videos"))
    parser.add_argument("--solo", default="", help="id de una sola película")
    args = parser.parse_args()

    dest_dir = Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with open(SOURCES, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r["id"] and r.get("usar", "si").strip().lower() == "si"
                and (not args.solo or r["id"] == args.solo)]

    errores = 0
    for r in rows:
        dest = dest_dir / f"{r['id']}.mp4"
        if dest.exists():
            print(f"[ok] {dest.name} ya existe")
        else:
            try:
                url = r.get("url_descarga", "").strip()
                if not url:
                    nombre = elegir_mp4(r["id"])
                    if nombre:
                        url = (f"https://archive.org/download/{r['id']}/"
                               f"{urllib.parse.quote(nombre)}")
                if url:
                    print(f"[descargando] {r['titulo']} ({r['anio']})  <- {url}")
                    descargar(url, dest)
                else:
                    errores += 1
                    print(f"[manual] {r['id']}: no hay .mp4; descárgalo desde {r['url_pagina']}")
            except Exception as e:  # noqa: BLE001
                errores += 1
                print(f"\n[error] {r['id']}: {e}", file=sys.stderr)
    print(f"Hecho: {len(rows)} películas, {errores} con problemas. Carpeta: {dest_dir}")


if __name__ == "__main__":
    main()
