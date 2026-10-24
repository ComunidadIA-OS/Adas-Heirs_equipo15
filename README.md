# [Nombre del proyecto] — Presencia y protagonismo de las mujeres en el cine

> Reto **"Mujeres por la IA Abierta"** (SEDIA · Comunidad IA de Código Abierto)
> Equipo: Kyara Gamarra Videla · Judith Caralt Rico · Luna Ospina Loaiza

<!-- TODO: frase del problema reformulado (1 línea). Ej:
"Medimos automáticamente cuánto aparecen las mujeres en las películas y con qué protagonismo visual,
para que filmotecas, festivales, productoras e investigadoras puedan auditar la representación en el cine." -->

## 1. Descripción de la solución

Sistema de IA abierto que analiza vídeos y calcula:

- **Presencia:** % de tiempo en pantalla y % de personas distintas por género percibido.
- **Protagonismo:** índice por persona a partir de tiempo en pantalla, tamaño en el encuadre,
  centralidad, planos en solitario y apariciones al principio/final.

Detalle de las métricas: [`docs/metricas.md`](docs/metricas.md).

### Pipeline

```
vídeo → muestreo de frames → detección de planos → detección de personas
      → tracking → análisis facial (género percibido) → agregación por trayectoria
      → métricas → informe / demo con revisión humana
```

| Módulo | Entrada | Salida |
|---|---|---|
| `src/shots.py` | vídeo | `planos.json` |
| `src/detection.py` | vídeo + planos | `detecciones.json` |
| `src/tracking.py` | detecciones | `tracks.json` |
| `src/faces.py` | vídeo + tracks | `caras.json` |
| `src/aggregation.py` | caras + tracks | `personas.json` |
| `src/metrics.py` | personas + tracks | `metricas.json` |

Todos los modelos se configuran en [`config/config.yaml`](config/config.yaml): cambiar de modelo = cambiar una línea.

## 2. Instalación

```bash
git clone <URL-del-repo>
cd reto-mujeres-ia-video
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # y rellenar el token de OVHcloud si se usa
```

## 3. Uso

```bash
# 1. Descargar vídeos listados en data/sources.csv
python scripts/download_videos.py

# 2. Procesar un vídeo (todas las etapas)
python -m src.pipeline --video data/videos/ejemplo.mp4

# 3. Solo algunas etapas (las demás se reutilizan de outputs/)
python -m src.pipeline --video data/videos/ejemplo.mp4 --steps aggregation,metrics

# 4. Demo con revisión humana
streamlit run app/app.py

# 5. Evaluar contra las anotaciones manuales
python scripts/evaluate.py --annotations data/annotations/anotaciones.csv

# 6. Resumen de todas las películas por década
python scripts/resumen_corpus.py
```

## 4. Datos

**17 películas de dominio público (1925–1968)** de la colección *Feature Films* de Internet Archive,
elegidas por décadas, calidad de imagen y variedad de géneros y repartos (`data/sources.csv`).
Hay 200 candidatas más en `data/candidatas_200.csv` para escalar. Los vídeos **no** se suben al
repositorio. Criterios, licencias y limitaciones: [`docs/datos_y_licencias.md`](docs/datos_y_licencias.md).

## 5. Resultados

<!-- TODO: tabla de métricas sobre el corpus y evaluación (precisión/recall del género percibido, etc.) -->

## 6. Perspectiva de género, ética y normativa

- [`docs/perspectiva_genero.md`](docs/perspectiva_genero.md)
- [`docs/etica_y_normativa.md`](docs/etica_y_normativa.md)
- [`docs/plan_despliegue.md`](docs/plan_despliegue.md)

## 7. Componentes de terceros y licencias

| Componente | Uso | Licencia |
|---|---|---|
| PyTorch / torchvision (Faster R-CNN) | Detección de personas | BSD-3-Clause |
| trackers (ByteTrack) | Tracking | Apache-2.0 |
| supervision | Estructuras de detección | MIT |
| PySceneDetect | Detección de planos | BSD-3-Clause |
| OpenCV | Lectura de vídeo | Apache-2.0 |
| InsightFace (código) | Análisis facial | MIT — **los modelos preentrenados son de uso no comercial; no se incluyen en el repo, se descargan aparte** |
| Streamlit | Demo | Apache-2.0 |
| <!-- TODO --> | | |

> Revisad esta tabla si cambiáis algún modelo. Ojo: Ultralytics YOLO es AGPL-3.0.

## 8. Declaración de uso de IA

<!-- TODO: indicar qué herramientas de IA se han usado en el desarrollo (asistentes de código, etc.). -->

## 9. Hoja de ruta

- [ ] Combinar con audio (quién habla) usando Whisper/diarización
- [ ] Re-identificación de personas entre planos
- [ ] Medida de incertidumbre por persona y por vídeo
- [ ] <!-- TODO -->

## 10. Licencia

[MIT](LICENSE)
