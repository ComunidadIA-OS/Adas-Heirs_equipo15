# Ada's Heirs — Presencia y protagonismo de las mujeres en el cine

> Reto **"Mujeres por la IA Abierta"** (SEDIA · Comunidad IA de Código Abierto)
> Equipo: Kyara Gamarra Videla · Judith Caralt Rico · Luna Ospina Loaiza

**Medimos automáticamente cuánto aparecen las mujeres en las películas y con qué protagonismo visual,
para que filmotecas, festivales, productoras e investigadoras puedan auditar la representación en el cine.**

## 1. Descripción de la solución

Sistema de IA abierto que analiza vídeos y calcula:

- **Presencia:** % de tiempo en pantalla y % de personas distintas por género percibido.
- **Protagonismo:** índice por persona a partir de tiempo en pantalla, tamaño en el encuadre,
  centralidad, planos en solitario y apariciones al principio/final.

Detalle de las métricas: [`docs/metricas.md`](docs/metricas.md).

### Pipeline

```
vídeo → muestreo de frames → detección de planos → detección de personas
      → tracking → análisis facial + modelo de visión (género percibido) → agregación por trayectoria
      → métricas → informe / demo con revisión humana
```

| Módulo | Entrada | Salida |
|---|---|---|
| `src/shots.py` | vídeo | `planos.json` |
| `src/detection.py` | vídeo + planos | `detecciones.json` |
| `src/tracking.py` | detecciones | `tracks.json` |
| `src/faces.py` | vídeo + tracks | `caras.json` |
| `src/vlm.py` | vídeo + tracks | `vlm.json` |
| `src/aggregation.py` | caras + vlm + tracks | `personas.json` |
| `src/metrics.py` | personas + tracks | `metricas.json` |

Todos los modelos se configuran en [`config/config.yaml`](config/config.yaml): cambiar de modelo = cambiar una línea.

**Género percibido (cómo se decide).** Para cada persona seguida, el modelo de visión (Qwen2.5-VL-72B, por
defecto) opina sobre hasta 6 recortes suyos; decide si al menos 2 respuestas coinciden y suponen el 60 % o
más. Si no decide, se usa el análisis facial (InsightFace) y, si tampoco decide, queda `no_determinado`.
Es percepción visual, no identidad. El modelo es intercambiable (cualquier modelo de visión con API
compatible con OpenAI) y la etapa se puede desactivar con `vlm.enabled: false`.

## 2. Instalación

```bash
git clone <URL-del-repo>
cd <carpeta-del-repo>
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OVH_AI_TOKEN="..."          # token de OVHcloud AI Endpoints para el modelo de visión (nunca en el repo)
```

## 3. Uso

```bash
# 1. Descargar vídeos listados en data/sources.csv
python scripts/download_videos.py

# 2. Procesar un vídeo (todas las etapas)
python -m src.pipeline --video data/videos/ejemplo.mp4

# 3. Solo algunas etapas (las demás se reutilizan de outputs/)
python -m src.pipeline --video data/videos/ejemplo.mp4 --steps aggregation,metrics
# Solo el modelo de visión + lo que depende de él (necesita OVH_AI_TOKEN; se reanuda si se corta)
python -m src.pipeline --video data/videos/ejemplo.mp4 --steps vlm,aggregation,metrics

# 4. Demo con revisión humana
streamlit run app/app.py

# 5. Evaluar el género contra las anotaciones manuales
python scripts/evaluate.py --annotations data/annotations/anotaciones.csv

# 6. Comparar el protagonismo del índice con el juicio humano
python scripts/protagonismo_vs_humano.py

# 7. Resumen de todas las películas por década
python scripts/resumen_corpus.py

# 8. Tests
pytest
```

## 4. Datos

**Películas de dominio público (1925–1968)** de la colección *Feature Films* de Internet Archive,
elegidas por décadas, calidad de imagen y variedad de géneros y repartos (`data/sources.csv`).
Hay 200 candidatas más en `data/candidatas_200.csv` para escalar. Los vídeos **no** se suben al
repositorio. Criterios, licencias y limitaciones: [`docs/datos_y_licencias.md`](docs/datos_y_licencias.md).

De las 17 películas seleccionadas, 14 se han procesado y 3 no. De las 14, **3 (*Detour*, *The General* y
*A Star Is Born*) se han procesado con el sistema final y se han evaluado con anotación humana**; las otras
11 solo tienen el análisis facial previo.

## 5. Resultados

### Evaluación del género percibido (anotación humana, 94 personas en 3 películas)

| | Mujeres | Hombres |
|---|---|---|
| Precisión | 1,00 | 0,92 |
| Recall | 0,85 (33 de 39) | 0,90 (47 de 52) |
| Sin decidir | 2 de 39 (5 %) | 5 de 52 (10 %) |

El sistema acierta 83 de 94 (88 %), se equivoca en 4 (4 %) y deja 7 sin decidir. **Los 4 errores son mujeres
percibidas como hombres**: el sistema tiende a infravalorar la presencia de mujeres. Por película y con la
discusión de sesgos: [`docs/perspectiva_genero.md`](docs/perspectiva_genero.md). Con el análisis facial solo
(sin modelo de visión), en *Detour* no se detectaba ninguna de las 4 mujeres anotadas.

Los parámetros del modelo de visión se eligieron con *Detour* y *The General*; *A Star Is Born* (color)
no se usó para elegirlos y es la medida más honesta (en ella se revisaron dos anotaciones tras compararlas
con el sistema). Muestras pequeñas: cifras orientativas.

### Validación del protagonismo (juicio humano, 94 personas en 3 películas)

La etiqueta "protagonista" del índice (umbral 0,5) coincide con nuestro juicio en 62 de 94 casos (**66 %**):
*Detour* 20 de 25 (80 %), *The General* 17 de 27 (63 %) y *A Star Is Born* 25 de 42 (60 %).

El índice es **conservador**: cuando marca a alguien como protagonista casi siempre coincidimos (17 de 18),
pero solo marca 17 de las 48 personas que nosotras consideramos protagonistas. Por eso los porcentajes de
protagonistas deben leerse como una **cota inferior**. Los pesos y el umbral se fijaron antes de anotar y no
se han ajustado a estas anotaciones. Detalle y posibles causas: [`docs/metricas.md`](docs/metricas.md).

### Presencia (tiempo en pantalla), con el sistema final

| Película | Mujeres | Hombres | Hombres/mujeres |
|---|---|---|---|
| The General (1926, muda) | 18,3 % | 75,2 % | 4,1 veces |
| A Star Is Born (1937, color) | 31,1 % | 59,4 % | 1,9 veces |
| Detour (1945, B/N) | 30,7 % | 64,9 % | 2,1 veces |

Referente: el Geena Davis Institute midió unas 2 veces más tiempo en pantalla para los personajes masculinos
en el cine actual. El resto del corpus (11 películas con solo el análisis facial previo y 3 sin procesar)
no se incluye porque no es comparable con el sistema final.

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
| InsightFace (código) | Análisis facial (respaldo del modelo de visión) | MIT — **los modelos preentrenados son de uso no comercial; no se incluyen en el repo, se descargan aparte** |
| Streamlit | Demo | Apache-2.0 |
| Qwen2.5-VL-72B-Instruct (vía OVHcloud AI Endpoints) | Género percibido (modelo de visión) | Licencia propia de Qwen: pesos abiertos, no OSI; uso comercial con condiciones |
| requests | Llamadas a la API del modelo de visión | Apache-2.0 |

> Revisad esta tabla si cambiáis algún modelo. Ojo: Ultralytics YOLO es AGPL-3.0.

## 8. Declaración de uso de IA

- **Claude (Anthropic)**, mediante Claude Code, se ha usado como asistente para escribir  parte
  del código del pipeline y la documentación. El equipo ha dirigido el diseño,
  ha tomado las decisiones (`docs/decisiones.md`), ha anotado a mano los datos de evaluación, ha medido los
  resultados y ha revisado los textos.
- **Modelos usados dentro del sistema:** Faster R-CNN (torchvision), ByteTrack, InsightFace y
  Qwen2.5-VL-72B-Instruct (OVHcloud AI Endpoints). Ver sección 7.

## 9. Hoja de ruta

- [ ] Combinar con audio (quién habla) usando Whisper/diarización
- [ ] Re-identificación de personas entre planos
- [ ] Medida de incertidumbre por persona y por vídeo
- [ ] Evaluar el sesgo por edad y tono de piel (p. ej. con FairFace) y con más anotadoras independientes
- [ ] Revisar el umbral y los pesos del índice de protagonismo con más anotaciones (hoy es conservador)
- [ ] Recortes de una sola persona con máscaras de segmentación (hoy las cajas solapadas dan recortes con dos personas)
- [ ] Probar otros modelos de visión abiertos con licencia OSI (p. ej. Mistral-Small-3.2, Apache-2.0)

## 10. Licencia

[MIT](LICENSE)

## 11. VÍDEO EXPLICATIVO
<https://drive.google.com/file/d/1f4Q3EypRORKyxUGcauRM9MrlsZAXM_Ax/view?usp=sharing>
