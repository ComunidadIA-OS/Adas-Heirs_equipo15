"""Prueba: modelo de visión (OVH AI Endpoints) como segundo voto de género PERCIBIDO.
Solo analiza los tracks anotados. No modifica el pipeline.
Uso (desde la raíz del proyecto):
  export OVH_AI_TOKEN="..."     # nunca en un archivo del repo
  python scripts/probar_vlm.py --video /workspace/videos/Detour.mp4 --model Mistral-Small-3.2-24B-Instruct-2506
"""
import argparse, base64, csv, json, os, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils import iter_frames, load_config, load_json  # noqa: E402

BASE_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
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


def ask(model, jpg, token):
    b64 = base64.b64encode(jpg).decode()
    payload = {"model": model, "temperature": 0, "max_tokens": 20,
               "messages": [{"role": "user", "content": [
                   {"type": "text", "text": PROMPT},
                   {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
    for attempt in range(5):
        r = requests.post(BASE_URL + "/chat/completions", json=payload, timeout=120,
                          headers={"Authorization": "Bearer " + token})
        if r.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Demasiados 429 (límite de peticiones)")


def vote(labels, threshold, min_votes):
    c = Counter(l for l in labels if l in ("mujer", "hombre"))
    n = sum(c.values())
    if n < min_votes:
        return ND
    top, k = c.most_common(1)[0]
    return top if k / n >= threshold else ND


def resumen(nombre, pred, real):
    ok = bad = nd = 0
    por = {"mujer": [0, 0, 0], "hombre": [0, 0, 0]}
    for tid, r in real.items():
        if r not in por:
            continue
        p = pred.get(tid, ND)
        i = 2 if p == ND else (0 if p == r else 1)
        por[r][i] += 1
        ok, bad, nd = ok + (i == 0), bad + (i == 1), nd + (i == 2)
    print(f"\n{nombre}: acierta {ok} | se equivoca {bad} | sin decidir {nd}")
    for g, (a, b, c) in por.items():
        print(f"   {g:7s}: {a} bien / {b} mal / {c} sin decidir (de {a + b + c})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--model", default="Mistral-Small-3.2-24B-Instruct-2506")
    ap.add_argument("--annotations", default="data/annotations/anotaciones.csv")
    ap.add_argument("--crops", type=int, default=4, help="recortes por track")
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--min-votes", type=int, default=2)
    args = ap.parse_args()

    token = os.environ.get("OVH_AI_TOKEN")
    if not token:
        sys.exit('Falta el token: export OVH_AI_TOKEN="..."')
    cfg = load_config()
    vid = Path(args.video).stem
    outdir = Path(cfg["paths"]["outputs"]) / vid
    real = {int(r["track_id"]): r["genero_percibido"].strip()
            for r in csv.DictReader(open(args.annotations, encoding="utf-8"))
            if r["video_id"] == vid and r["genero_percibido"].strip()}
    if not real:
        sys.exit(f"No hay anotaciones de {vid} en {args.annotations}")
    tracks = load_json(outdir / "tracks.json")
    personas = {p["track_id"]: p["label"] for p in load_json(outdir / "personas.json")["personas"]}

    by_track = defaultdict(list)
    for o in tracks["observations"]:
        if o["track_id"] in real:
            by_track[o["track_id"]].append(o)
    need = defaultdict(list)
    for tid, obs in by_track.items():
        obs.sort(key=lambda o: (o["box"][2] - o["box"][0]) * (o["box"][3] - o["box"][1]), reverse=True)
        for o in obs[:args.crops]:
            need[o["frame"]].append((tid, o["box"]))

    answers = defaultdict(list)
    last = max(need) if need else -1
    for idx, _, frame, scale in iter_frames(args.video, cfg["video"]["fps_sample"], cfg["video"]["max_side"]):
        if idx > last:
            break
        for tid, box in need.get(idx, []):
            x1, y1, x2, y2 = [int(v * scale) for v in box]
            pad = int(0.1 * max(x2 - x1, y2 - y1))
            h, w = frame.shape[:2]
            crop = frame[max(0, y1 - pad):min(h, y2 + pad), max(0, x1 - pad):min(w, x2 + pad)]
            if crop.size == 0:
                continue
            k = 1.0
            if min(crop.shape[:2]) < 224:
                k = min(4.0, 224 / min(crop.shape[:2]))
            elif max(crop.shape[:2]) > 512:
                k = 512 / max(crop.shape[:2])
            if k != 1.0:
                crop = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
            ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
            answers[tid].append(parse(ask(args.model, buf.tobytes(), token)))

    vlm = {tid: vote(a, args.threshold, args.min_votes) for tid, a in answers.items()}
    fusion = {tid: (personas.get(tid, ND) if personas.get(tid, ND) != ND else vlm.get(tid, ND))
              for tid in real}
    print(f"{'track':>8} {'tú':<15} {'insightface':<15} {'visión':<15} votos visión")
    for tid in sorted(real):
        print(f"{tid:>8} {real[tid]:<15} {personas.get(tid, '-'):<15} {vlm.get(tid, '-'):<15} "
              f"{dict(Counter(answers.get(tid, [])))}")
    resumen("InsightFace (actual)", personas, real)
    resumen("Modelo de visión", vlm, real)
    resumen("Fusión (cara y, si no decide, visión)", fusion, real)
    json.dump({"modelo": args.model, "respuestas": answers, "vlm": vlm, "fusion": fusion},
              open(outdir / "vlm_prueba.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
