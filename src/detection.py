"""Etapa 2 — Detección de personas frame a frame.

Salida: detecciones.json
  {"video": ..., "width": W, "height": H, "fps_sample": 2,
   "frames": [{"frame": 0, "t": 0.0, "shot_id": 0,
               "boxes": [[x1, y1, x2, y2, score], ...]}, ...]}

Las cajas están en píxeles de la resolución ORIGINAL del vídeo.
Para añadir otro detector: crea una clase con método detect(frame_bgr) -> lista de [x1,y1,x2,y2,score]
y regístrala en get_detector().
"""

from .utils import iter_frames, load_json, resolve_device, save_json, shot_for_time, video_info


class TorchvisionFasterRCNN:
    """Faster R-CNN preentrenado en COCO (torchvision, licencia BSD). Clase 1 = persona."""

    PERSON_LABEL = 1

    def __init__(self, min_score=0.6, device="auto"):
        import torch
        from torchvision.models.detection import (FasterRCNN_ResNet50_FPN_V2_Weights,
                                                  fasterrcnn_resnet50_fpn_v2)
        self.torch = torch
        self.device = resolve_device(device)
        weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        self.model = fasterrcnn_resnet50_fpn_v2(weights=weights).to(self.device).eval()
        self.min_score = min_score

    def detect(self, frame_bgr):
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)   # OpenCV lee en BGR
        tensor = self.torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).to(self.device)
        with self.torch.no_grad():
            out = self.model([tensor])[0]
        boxes = []
        for box, label, score in zip(out["boxes"], out["labels"], out["scores"]):
            if int(label) == self.PERSON_LABEL and float(score) >= self.min_score:
                x1, y1, x2, y2 = [float(v) for v in box]
                boxes.append([x1, y1, x2, y2, float(score)])
        return boxes


def get_detector(cfg):
    det_cfg = cfg["detection"]
    if det_cfg["model"] == "torchvision_fasterrcnn":
        return TorchvisionFasterRCNN(min_score=det_cfg["min_score"], device=det_cfg["device"])
    raise ValueError(f"Detector desconocido: {det_cfg['model']}")


def run(video_path, cfg, outdir):
    info = video_info(video_path)
    shots = load_json(outdir / "planos.json")["shots"]
    detector = get_detector(cfg)
    min_area = cfg["detection"]["min_box_ratio"] * info["width"] * info["height"]

    frames = []
    for idx, t, frame, scale in iter_frames(video_path, cfg["video"]["fps_sample"],
                                            cfg["video"]["max_side"]):
        boxes = []
        for x1, y1, x2, y2, s in detector.detect(frame):
            x1, y1, x2, y2 = x1 / scale, y1 / scale, x2 / scale, y2 / scale
            if (x2 - x1) * (y2 - y1) >= min_area:
                boxes.append([x1, y1, x2, y2, s])
        frames.append({"frame": idx, "t": t, "shot_id": shot_for_time(shots, t), "boxes": boxes})

    result = {"video": str(video_path), "width": info["width"], "height": info["height"],
              "fps_sample": cfg["video"]["fps_sample"], "duration_s": info["duration_s"],
              "frames": frames}
    save_json(result, outdir / "detecciones.json")
    n = sum(len(f["boxes"]) for f in frames)
    print(f"[detection] {len(frames)} frames analizados, {n} detecciones de persona")
    return result
