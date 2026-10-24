# Anotaciones manuales (ground truth)

Sirven para **evaluar** el sistema. Hay que anotar a mano 10–15 clips cortos.

## Cómo anotar

1. Procesa el clip: `python -m src.pipeline --video data/videos/<id>.mp4`
2. Abre `outputs/<id>/personas.json` y la demo (`streamlit run app/app.py`) para ver los `track_id`.
3. Para cada persona, añade una fila en `anotaciones.csv`:

| columna | valores |
|---|---|
| `video_id` | nombre del vídeo sin `.mp4` |
| `track_id` | ID de la trayectoria |
| `genero_percibido` | `mujer` / `hombre` / `no_determinado` |
| `protagonista` | `si` / `no` (vuestro juicio humano) |
| `notas` | lo que queráis (p. ej. "de perfil todo el rato") |

4. Evalúa: `python scripts/evaluate.py`

## Reglas

- Anotad **género percibido**, igual que el modelo. Si dudáis, `no_determinado`.
- Que anoten al menos **dos personas del equipo** un par de clips y comparad: si no coincidís,
  la métrica es ambigua (eso también es un resultado a contar).
- Anotad unos minutos de 2–3 películas de épocas distintas (una muda, una en color, una de cine negro).
- No guardéis nombres de personas en este CSV si no hace falta.
