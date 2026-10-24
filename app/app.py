"""Demo con supervisión humana.

Uso:  streamlit run app/app.py

1. Elige un vídeo ya procesado (carpeta en outputs/).
2. Revisa la tabla de personas: puedes CORREGIR la etiqueta de género percibido.
3. "Guardar revisión" crea personas_revisado.json y recalcula las métricas con tus correcciones.

Así una persona puede aceptar o rechazar lo que dice la IA antes de dar el informe por bueno
(supervisión humana, marco ético europeo).
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import metrics  # noqa: E402
from src.utils import load_config, load_json, save_json  # noqa: E402

cfg = load_config()
outputs = Path(cfg["paths"]["outputs"])

st.set_page_config(page_title="Presencia de mujeres en vídeo", layout="wide")
st.title("Presencia y protagonismo de las mujeres en vídeo")
st.caption("Género PERCIBIDO por un modelo automático. Revisa y corrige antes de usar los resultados.")

videos = sorted(p.name for p in outputs.iterdir() if (p / "metricas.json").exists()) \
    if outputs.exists() else []
if not videos:
    st.info("No hay vídeos procesados. Ejecuta: python -m src.pipeline --video <ruta>")
    st.stop()

video = st.selectbox("Vídeo", videos)
vdir = outputs / video
result = load_json(vdir / "metricas.json")

st.subheader("Resumen por género percibido")
st.caption(f"Etiquetas usadas: {result.get('fuente_etiquetas', 'personas.json')}")
por_genero = pd.DataFrame(result["por_genero"]).T
st.dataframe(por_genero, use_container_width=True)

c1, c2 = st.columns(2)
c1.markdown("**% de tiempo en pantalla**")
c1.bar_chart(por_genero["pct_screen_time"])
c2.markdown("**Índice de protagonismo medio**")
c2.bar_chart(por_genero["protagonism_medio"])

st.subheader("Personas detectadas (revisión humana)")
df = pd.DataFrame(result["personas"])
edited = st.data_editor(
    df,
    column_config={"label": st.column_config.SelectboxColumn(
        "Género percibido", options=["mujer", "hombre", "no_determinado"])},
    disabled=[c for c in df.columns if c != "label"],
    use_container_width=True,
)

if st.button("Guardar revisión y recalcular"):
    personas = [{"track_id": int(r.track_id), "label": r.label, "revisado": True}
                for r in edited.itertuples()]
    save_json({"personas": personas}, vdir / "personas_revisado.json")
    tracks = load_json(vdir / "tracks.json")
    new = metrics.compute(tracks, personas, cfg["metrics"])
    new["fuente_etiquetas"] = "personas_revisado.json"
    save_json(new, vdir / "metricas.json")
    st.success("Revisión guardada. Recarga la página para ver las métricas actualizadas.")
