"""Descarga los vídeos listados en data/sources.csv a data/videos/.

Solo se descargan las filas con usar = si. Rellena 'url_descarga' con el enlace directo al .mp4
(en la ficha de Internet Archive: "DOWNLOAD OPTIONS" -> MPEG4, botón derecho -> copiar enlace).
Si no hay enlace directo, descarga el vídeo a mano y guárdalo como data/videos/<id>.mp4.
"""

import csv
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.csv"
VIDEOS = ROOT / "data" / "videos"


def main():
    VIDEOS.mkdir(parents=True, exist_ok=True)
    with open(SOURCES, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["id"] and r.get("usar", "si").strip().lower() == "si"]
    for r in rows:
        dest = VIDEOS / f"{r['id']}.mp4"
        if dest.exists():
            print(f"[ok] {dest.name} ya existe")
            continue
        url = r.get("url_descarga", "").strip()
        if not url:
            print(f"[manual] {r['id']}: descárgalo desde {r['url_pagina']} y guárdalo como {dest}")
            continue
        print(f"[descargando] {r['id']} ...")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as e:  # noqa: BLE001
            print(f"[error] {r['id']}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
