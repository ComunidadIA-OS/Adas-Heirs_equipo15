"""Etapa 3 — Tracking: une las detecciones de cada frame en trayectorias con ID.

El tracker se reinicia en cada plano: una persona no se "sigue" a través de un corte de cámara.
Los IDs son únicos en todo el vídeo: track_id = shot_id * 10000 + id_local.

Salida: tracks.json
  {"video": ..., "width": W, "height": H, "fps_sample": 2, "duration_s": ...,
   "observations": [{"frame": 0, "t": 0.0, "shot_id": 0, "track_id": 10001,
                     "box": [x1, y1, x2, y2], "score": 0.93}, ...]}
"""

from collections import Counter

import numpy as np

from .utils import load_json, save_json


def _new_tracker(cfg):
    """ByteTrack del paquete 'trackers' de Roboflow (Apache-2.0)."""
    if cfg["tracking"]["model"] != "bytetrack":
        raise ValueError(f"Tracker desconocido: {cfg['tracking']['model']}")
    from trackers import ByteTrackTracker
    return ByteTrackTracker(frame_rate=cfg["video"]["fps_sample"],
                            track_activation_threshold=cfg["tracking"]["activation_threshold"],
                            lost_track_buffer=cfg["tracking"]["lost_track_buffer"])


def run(video_path, cfg, outdir):
    import supervision as sv

    det = load_json(outdir / "detecciones.json")
    observations = []
    tracker = None
    current_shot = None

    for f in det["frames"]:
        if f["shot_id"] != current_shot:          # corte de plano -> tracker nuevo
            tracker = _new_tracker(cfg)
            current_shot = f["shot_id"]
        if not f["boxes"]:
            boxes = np.empty((0, 4))
            scores = np.empty((0,))
        else:
            arr = np.array(f["boxes"], dtype=float)
            boxes, scores = arr[:, :4], arr[:, 4]
        dets = sv.Detections(xyxy=boxes, confidence=scores,
                             class_id=np.zeros(len(scores), dtype=int))
        tracked = tracker.update(dets)
        for box, tid, score in zip(tracked.xyxy, tracked.tracker_id, tracked.confidence):
            if tid is None or int(tid) < 0:        # trayectoria aún no confirmada
                continue
            observations.append({
                "frame": f["frame"], "t": f["t"], "shot_id": f["shot_id"],
                "track_id": int(f["shot_id"]) * 10000 + int(tid),
                "box": [float(v) for v in box], "score": float(score),
            })

    # Descartar trayectorias demasiado cortas (ruido)
    counts = Counter(o["track_id"] for o in observations)
    min_frames = cfg["tracking"]["min_track_frames"]
    observations = [o for o in observations if counts[o["track_id"]] >= min_frames]

    result = {k: det[k] for k in ("video", "width", "height", "fps_sample", "duration_s")}
    result["observations"] = observations
    save_json(result, outdir / "tracks.json")
    print(f"[tracking] {len({o['track_id'] for o in observations})} trayectorias")
    return result
