"""Etapa 4b — Segunda opinión de género PERCIBIDO con un modelo de visión (OVH AI Endpoints).

Para cada persona seguida (track) se recortan sus K apariciones más grandes y se le pregunta a un
modelo de visión abierto (API compatible con OpenAI) cómo percibiría el género de la persona
por su aspecto (cara, pelo, ropa, complexión). Es PERCEPCIÓN VISUAL, no identidad.

- El token se lee SIEMPRE de una variable de entorno (por defecto OVH_AI_TOKEN). Nunca en el repo.
- Los recortes se envían al servicio, no se guardan en disco.
- Modelo intercambiable: cambia `vlm.model` en config/config.yaml (cualquier modelo de visión
  compatible con la API de OpenAI).

Salida: vlm.json
  {"modelo": "...", "crops_por_track": 6, "answers": {"<track_id>": ["mujer", "hombre", ...]}}
Si el proceso se interrumpe, se guarda vlm_parcial.json y al repetir la etapa se reanuda.

Combinación con la cara (función combine, usada por la etapa de agregación):
- Si los votos del modelo de visión superan el umbral -> esa etiqueta (fuente "vlm").
- Si no -> se mantiene la etiqueta del análisis facial (fuente "cara").
"""

import base64
import os
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .utils import iter_frames, load_json, save_json

ND = "no_determinado"
PROMPT = (
    "Esta imagen es un recorte de una película antigua y muestra a UNA persona. "
    "Indica el género con el que una persona OBSERVADORA percibiría a esta persona por su aspecto "
    "(cara, pelo, ropa, complexión). No es identidad, solo percepción visual. "
    "Responde con una sola palabra: mujer, hombre o no_determinado "
    "(usa no_determinado solo si no hay pistas suficientes: muy pequeña, muy oscura o cortada)."
)


def parse(text):
    t = (text or "").lower()
    if "no_determinado" in t or "no determinado" in t:
        return ND
    m, h = "mujer" in t, "hombre" in t
    if m and not h:
        return "mujer"
    if h and not m:
        return "hombre"
    return ND


def vote(labels, threshold, min_votes):
    """Mayoría entre las respuestas 'mujer'/'hombre'; 'no_determinado' no cuenta como voto."""
    c = Counter(l for l in labels if l in ("mujer", "hombre"))
    n = sum(c.values())
    if n < min_votes:
        return ND
    top, k = c.most_common(1)[0]
    return top if k / n >= threshold else ND


def _ask(vcfg, token, jpg):
    import requests
    b64 = base64.b64encode(jpg).decode()
    payload = {"model": vcfg["model"], "temperature": 0, "max_tokens": 20,
               "messages": [{"role": "user", "content": [
                   {"type": "text", "text": PROMPT},
                   {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
    url = vcfg.get("base_url", "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1").rstrip("/")
    for attempt in range(6):
        try:
            r = requests.post(url + "/chat/completions", json=payload, timeout=120,
                              headers={"Authorization": "Bearer " + token})
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(4 * (attempt + 1))
                continue
            r.raise_for_status()
            return parse(r.json()["choices"][0]["message"]["content"])
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None   # no se pudo: no cuenta como voto y la etapa se podrá reanudar


def _crop_jpeg(frame, box, scale):
    import cv2
    x1, y1, x2, y2 = [int(v * scale) for v in box]
    pad = int(0.1 * max(x2 - x1, y2 - y1))
    h, w = frame.shape[:2]
    crop = frame[max(0, y1 - pad):min(h, y2 + pad), max(0, x1 - pad):min(w, x2 + pad)]
    if crop.size == 0:
        return None
    k = 1.0
    if min(crop.shape[:2]) < 224:
        k = min(4.0, 224 / min(crop.shape[:2]))
    elif max(crop.shape[:2]) > 512:
        k = 512 / max(crop.shape[:2])
    if k != 1.0:
        crop = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
    ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return buf.tobytes() if ok else None


def run(video_path, cfg, outdir):
    vcfg = cfg.get("vlm") or {}
    outdir = Path(outdir)
    out = outdir / "vlm.json"
    if not vcfg.get("enabled", False):
        save_json({"modelo": None, "crops_por_track": 0, "answers": {}}, out)
        print("[vlm] desactivado (vlm.enabled: false)")
        return {}
    token = os.environ.get(vcfg.get("token_env", "OVH_AI_TOKEN"))
    if not token:
        raise RuntimeError("Falta el token del modelo de visión: export "
                           f"{vcfg.get('token_env', 'OVH_AI_TOKEN')}=\"...\" (nunca en un archivo)")
    K = int(vcfg.get("crops_per_track", 6))
    workers = int(vcfg.get("workers", 6))
    tracks = load_json(outdir / "tracks.json")
    partial = outdir / "vlm_parcial.json"
    # Reanuda: parte de lo ya contestado (parcial o vlm.json previo del mismo modelo) y solo pide lo que falta
    answers = {}
    if partial.exists():
        answers = load_json(partial)["answers"]
    elif out.exists() and load_json(out).get("modelo") == vcfg["model"]:
        answers = load_json(out).get("answers", {})

    by_track = defaultdict(list)
    for o in tracks["observations"]:
        by_track[o["track_id"]].append(o)
    need = defaultdict(list)
    total = 0
    for tid, obs in by_track.items():
        want = min(K, len(obs))
        if len(answers.get(str(tid), [])) >= want:
            continue
        answers.pop(str(tid), None)
        obs.sort(key=lambda o: (o["box"][2] - o["box"][0]) * (o["box"][3] - o["box"][1]), reverse=True)
        for o in obs[:K]:
            need[o["frame"]].append((tid, o["box"]))
            total += 1
    print(f"[vlm] {len(by_track)} personas, {total} recortes por analizar con {vcfg['model']}")

    lock = threading.Lock()
    gate = threading.BoundedSemaphore(workers * 3)
    done = [0]

    def task(tid, jpg):
        try:
            label = _ask(vcfg, token, jpg)
            with lock:
                if label is not None:
                    answers.setdefault(str(tid), []).append(label)
                done[0] += 1
                if done[0] % 100 == 0:
                    save_json({"answers": answers}, partial)
                    print(f"[vlm] {done[0]}/{total} recortes")
        finally:
            gate.release()

    last = max(need) if need else -1
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for idx, _, frame, scale in iter_frames(video_path, cfg["video"]["fps_sample"],
                                                cfg["video"]["max_side"]):
            if idx > last:
                break
            for tid, box in need.get(idx, []):
                jpg = _crop_jpeg(frame, box, scale)
                if jpg is None:
                    continue
                gate.acquire()
                pool.submit(task, tid, jpg)

    result = {"modelo": vcfg["model"], "crops_por_track": K, "answers": answers}
    save_json(result, out)
    if partial.exists():
        partial.unlink()
    pend = sum(1 for tid, obs in by_track.items() if len(answers.get(str(tid), [])) < min(K, len(obs)))
    if pend:
        print(f"[vlm] AVISO: {pend} personas con respuestas incompletas (fallos de red o de límite). "
              "Vuelve a ejecutar la etapa vlm: solo pedirá lo que falta.")
    n_ok = sum(1 for tid, a in answers.items()
               if vote(a, vcfg.get("vote_threshold", 0.6), vcfg.get("min_votes", 2)) != ND)
    print(f"[vlm] {len(answers)} personas con respuestas; {n_ok} con etiqueta decidida")
    return result


def combine(personas, outdir, cfg):
    """Combina la agregación facial con la opinión del modelo de visión (prioridad al modelo de visión)."""
    vcfg = cfg.get("vlm") or {}
    f = Path(outdir) / "vlm.json"
    if not vcfg.get("enabled", False) or not f.exists():
        return personas
    answers = load_json(f).get("answers", {})
    th, mv = vcfg.get("vote_threshold", 0.6), vcfg.get("min_votes", 2)
    out = []
    for p in personas:
        labels = answers.get(str(p["track_id"]), [])
        c = Counter(l for l in labels if l in ("mujer", "hombre"))
        lab = vote(labels, th, mv)
        q = dict(p)
        q["label_cara"] = p["label"]
        q["votes_vlm"] = dict(c)
        if lab != ND:
            q["label"] = lab
            q["confidence"] = round(c[lab] / sum(c.values()), 3)
            q["fuente"] = "vlm"
        else:
            q["fuente"] = "cara"
        out.append(q)
    return out
