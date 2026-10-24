"""Utilidades comunes: configuración, lectura/escritura de JSON y lectura de frames."""

import json
from pathlib import Path

import yaml


def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def video_outdir(cfg, video_path):
    """Carpeta de resultados de un vídeo: outputs/<nombre_del_video>/"""
    out = Path(cfg["paths"]["outputs"]) / Path(video_path).stem
    out.mkdir(parents=True, exist_ok=True)
    return out


def resolve_device(device):
    if device != "auto":
        return device
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def video_info(video_path):
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS) or 25.0,
        "n_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }
    cap.release()
    info["duration_s"] = info["n_frames"] / info["fps"] if info["fps"] else 0.0
    return info


def iter_frames(video_path, fps_sample, max_side=0):
    """Devuelve (indice_frame, tiempo_s, imagen_BGR, escala) muestreando a fps_sample.

    'escala' es el factor aplicado si se redimensiona (para convertir cajas a la resolución original).
    """
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    native_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, round(native_fps / fps_sample))
    idx = 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if idx % step == 0:
            ok, frame = cap.retrieve()
            if not ok:
                break
            scale = 1.0
            h, w = frame.shape[:2]
            if max_side and max(h, w) > max_side:
                scale = max_side / max(h, w)
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
            yield idx, idx / native_fps, frame, scale
        idx += 1
    cap.release()


def shot_for_time(shots, t):
    """Devuelve el shot_id que contiene el instante t (o 0 si no hay planos)."""
    for s in shots:
        if s["start_s"] <= t < s["end_s"]:
            return s["shot_id"]
    return shots[-1]["shot_id"] if shots else 0
