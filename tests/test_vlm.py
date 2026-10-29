"""Tests de la lógica del modelo de visión que no necesita red ni modelos: parseo, votación y combinación.

Ejecutar:  pytest
"""

import json

from src.vlm import ND, combine, parse, vote

CFG = {"vlm": {"enabled": True, "vote_threshold": 0.6, "min_votes": 2}}


def test_parse_respuestas():
    assert parse("Mujer") == "mujer"
    assert parse("hombre.") == "hombre"
    assert parse("no_determinado") == ND
    assert parse("no determinado") == ND
    assert parse("") == ND
    assert parse(None) == ND
    assert parse("mujer u hombre") == ND          # ambigua: no se fuerza


def test_voto_mayoria_clara():
    assert vote(["mujer"] * 5 + ["hombre"], 0.6, 2) == "mujer"


def test_voto_sin_mayoria_es_no_determinado():
    assert vote(["mujer", "hombre"], 0.6, 2) == ND
    assert vote(["mujer"] * 5 + ["hombre"] * 5, 0.6, 2) == ND


def test_pocos_votos_es_no_determinado():
    assert vote(["mujer"], 0.6, 2) == ND
    assert vote([], 0.6, 2) == ND


def test_no_determinado_no_cuenta_como_voto():
    assert vote([ND, ND, ND, "mujer"], 0.6, 2) == ND
    assert vote([ND, "hombre", "hombre"], 0.6, 2) == "hombre"


def _persona(tid, label):
    return {"track_id": tid, "label": label, "confidence": 0.5, "votes": {}, "n_faces": 0, "age_median": None}


def test_combine_prioriza_vision_y_conserva_cara_como_respaldo(tmp_path):
    (tmp_path / "vlm.json").write_text(json.dumps(
        {"modelo": "x", "crops_por_track": 6,
         "answers": {"1": ["mujer"] * 5, "2": ["hombre"], "3": ["mujer", "hombre"]}}))
    personas = [_persona(1, "hombre"), _persona(2, "hombre"), _persona(3, ND), _persona(4, "mujer")]
    out = {p["track_id"]: p for p in combine(personas, tmp_path, CFG)}
    assert out[1]["label"] == "mujer" and out[1]["fuente"] == "vlm" and out[1]["label_cara"] == "hombre"
    assert out[2]["label"] == "hombre" and out[2]["fuente"] == "cara"    # 1 voto: usa la cara
    assert out[3]["label"] == ND and out[3]["fuente"] == "cara"          # empate: no se fuerza
    assert out[4]["label"] == "mujer" and out[4]["fuente"] == "cara"     # sin respuestas: usa la cara


def test_combine_desactivado_no_cambia_nada(tmp_path):
    personas = [_persona(1, "hombre")]
    assert combine(personas, tmp_path, {"vlm": {"enabled": False}}) == personas
    assert combine(personas, tmp_path, {}) == personas