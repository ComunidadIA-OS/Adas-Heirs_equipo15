"""Tests de la lógica que no necesita modelos: agregación y métricas.

Ejecutar:  pytest
"""

from src.aggregation import UNKNOWN, aggregate_track
from src.metrics import compute

MCFG = {"edge_fraction": 0.1, "protagonist_threshold": 0.5,
        "weights": {"screen_time": 0.3, "size": 0.2, "centrality": 0.15, "solo": 0.2, "edges": 0.15}}


def test_votacion_clara():
    obs = [{"gender": "mujer", "age": 40}] * 9 + [{"gender": "hombre", "age": 42}]
    r = aggregate_track(obs, vote_threshold=0.8, min_votes=3)
    assert r["label"] == "mujer"
    assert r["confidence"] == 0.9


def test_votacion_dudosa_es_no_determinado():
    obs = [{"gender": "mujer"}] * 6 + [{"gender": "hombre"}] * 4
    assert aggregate_track(obs, 0.8, 3)["label"] == UNKNOWN


def test_pocas_caras_es_no_determinado():
    assert aggregate_track([{"gender": "mujer"}] * 2, 0.8, 3)["label"] == UNKNOWN


def _obs(track, frame, box, shot=0):
    return {"frame": frame, "t": frame / 2, "shot_id": shot, "track_id": track, "box": box}


def test_metricas_persona_central_y_sola_es_mas_protagonista():
    # Persona 1: grande, centrada, sola, todo el vídeo. Persona 2: pequeña, en una esquina, poco rato.
    obs = [_obs(1, f, [700, 300, 1220, 1000]) for f in range(0, 20)]
    obs += [_obs(2, f, [0, 0, 100, 150]) for f in range(8, 11)]
    tracks = {"width": 1920, "height": 1080, "fps_sample": 2, "duration_s": 10.0,
              "observations": obs}
    personas = [{"track_id": 1, "label": "mujer"}, {"track_id": 2, "label": "hombre"}]
    res = compute(tracks, personas, MCFG)
    p = {r["track_id"]: r for r in res["personas"]}
    assert p[1]["protagonism"] > p[2]["protagonism"]
    assert p[1]["protagonist"] and not p[2]["protagonist"]
    assert res["por_genero"]["mujer"]["pct_screen_time"] > 80
