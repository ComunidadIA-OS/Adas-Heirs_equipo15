"""Etapa 1 — Detección de planos (cortes de cámara).

Salida: planos.json
  {"video": ..., "duration_s": ..., "shots": [{"shot_id": 0, "start_s": 0.0, "end_s": 12.4}, ...]}
"""

from . import utils
from .utils import save_json, video_info


def detect_shots(video_path, cfg):
    info = video_info(video_path)
    shots_cfg = cfg["shots"]

    if not shots_cfg.get("enabled", True):
        return [{"shot_id": 0, "start_s": 0.0, "end_s": info["duration_s"]}]

    try:
        from scenedetect import AdaptiveDetector, ContentDetector, detect
    except ImportError:
        print("[shots] PySceneDetect no instalado: se trata el vídeo como un único plano.")
        return [{"shot_id": 0, "start_s": 0.0, "end_s": info["duration_s"]}]

    min_len = int(shots_cfg["min_shot_s"] * info["fps"])
    luma_only = shots_cfg.get("luma_only", True)   # True: mejor para cine en blanco y negro
    if shots_cfg.get("detector", "adaptive") == "adaptive":
        detector = AdaptiveDetector(min_scene_len=min_len, luma_only=luma_only)
    else:
        detector = ContentDetector(threshold=shots_cfg["threshold"], min_scene_len=min_len,
                                   luma_only=luma_only)
    scenes = detect(
        str(video_path),
        detector,
        end_time=utils.MAX_SECONDS or None,
    )
    if not scenes:
        return [{"shot_id": 0, "start_s": 0.0, "end_s": info["duration_s"]}]

    return [
        {"shot_id": i, "start_s": start.get_seconds(), "end_s": end.get_seconds()}
        for i, (start, end) in enumerate(scenes)
    ]


def run(video_path, cfg, outdir):
    info = video_info(video_path)
    shots = detect_shots(video_path, cfg)
    result = {"video": str(video_path), "duration_s": info["duration_s"], "shots": shots}
    save_json(result, outdir / "planos.json")
    print(f"[shots] {len(shots)} planos detectados")
    return result
