"""Ejecuta el pipeline completo o algunas etapas.

Uso:
  python -m src.pipeline --video data/videos/ejemplo.mp4
  python -m src.pipeline --video data/videos/ejemplo.mp4 --steps aggregation,metrics
  python -m src.pipeline --video data/videos/ejemplo.mp4 --force   # rehace aunque ya exista

Cada etapa guarda su JSON en outputs/<nombre_video>/. Si el JSON ya existe, la etapa se salta
(salvo --force o si la pides explícitamente con --steps).
"""

import argparse

from . import aggregation, detection, faces, metrics, shots, tracking
from .utils import load_config, set_max_seconds, video_outdir

STEPS = [
    ("shots", shots, "planos.json"),
    ("detection", detection, "detecciones.json"),
    ("tracking", tracking, "tracks.json"),
    ("faces", faces, "caras.json"),
    ("aggregation", aggregation, "personas.json"),
    ("metrics", metrics, "metricas.json"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--video", required=True)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--steps", default="all", help="lista separada por comas o 'all'")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    set_max_seconds(cfg["video"].get("max_seconds", 0))
    if cfg["video"].get("max_seconds"):
        print(f"Modo prueba: solo se analizan los primeros {cfg['video']['max_seconds']} s")
    outdir = video_outdir(cfg, args.video)
    requested = None if args.steps == "all" else set(args.steps.split(","))

    for name, module, output in STEPS:
        explicitly = requested is not None and name in requested
        if requested is not None and not explicitly:
            continue
        if (outdir / output).exists() and not (args.force or explicitly):
            print(f"[{name}] ya existe {output}, se reutiliza")
            continue
        module.run(args.video, cfg, outdir)

    print(f"Resultados en {outdir}")


if __name__ == "__main__":
    main()
