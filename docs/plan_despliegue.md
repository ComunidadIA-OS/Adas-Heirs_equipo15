# Plan de puesta en producción

## Usuarios y caso de uso

| Usuario | Para qué lo usa | Qué información ve |
|---|---|---|
| Filmotecas y archivos (p. ej. Filmoteca Española, filmotecas autonómicas) | Analizar la representación en sus fondos por época | Informe agregado por década/género |
| Festivales y premios de cine | Ofrecer un indicador de representación de las películas presentadas | Métricas por película |
| Productoras y plataformas | Autoevaluar sus producciones antes del estreno | Informe + revisión humana |
| Investigadoras y docentes de estudios de cine y género | Estudios cuantitativos reproducibles | Datos agregados abiertos |

## Dónde interviene la persona (supervisión humana)

1. El sistema procesa el vídeo y propone etiquetas y métricas.
2. Una persona revisa en la demo las etiquetas dudosas y las corrige.
3. Solo entonces se genera el informe final.

## Infraestructura

- Desarrollo: local con muestras pequeñas.
- Procesamiento: GPU en OVHcloud (2× V100S) para detección, seguimiento y análisis facial, y
  OVHcloud AI Endpoints (API compatible con OpenAI) para el modelo de visión.
- **Tiempo medido:** el análisis de personas (planos, detección, seguimiento y caras) de las 14 películas
  procesadas tardó unas 2 horas en la GPU. El modelo de visión añade, por película, entre 7 y unos 50 minutos
  según el número de personas seguidas (*Detour*: 3.792 llamadas en 13 min; *The General*: 2.478 en 7 min;
  *A Star Is Born*: más de 11.000 llamadas, menos de una hora). La velocidad real fue de 300–400 llamadas
  por minuto.
- **Límites:** 400 llamadas por minuto por modelo y 10 MB por petición (OVH AI Endpoints). La etapa guarda
  progreso cada 100 recortes y se reanuda sola si se corta.
- **Coste:** durante el reto el uso es gratuito con límites. En producción se paga por uso del endpoint: una
  película de 1–2 horas necesita entre 2.500 y más de 11.000 llamadas, con una imagen pequeña cada una.
  El coste exacto se calcula con la tarifa vigente de OVH para el modelo elegido; no lo hemos medido en euros.
- **Alternativa sin API:** como el modelo es intercambiable (`vlm.model` en `config/config.yaml`), una
  institución con GPU puede alojar un modelo de visión abierto propio y apuntar `vlm.base_url` a su servidor.

## Permisos y acuerdos necesarios

- Películas de dominio público: comprobar la licencia de cada una (y su estado en la UE).
- Archivo de filmotecas o catálogos comerciales: **acuerdo previo** con el titular de los derechos.
- Televisiones: **acuerdo previo** con la cadena para acceder a su archivo mediante API; nunca scraping.
- Modelos de terceros: revisar licencias. InsightFace = uso no comercial (para uso comercial, desactivarlo
  con `faces.model: none` y usar solo el modelo de visión, o sustituirlo). Qwen2.5-VL-72B se distribuye
  con la licencia propia de Qwen (pesos abiertos, no OSI; permite uso comercial con condiciones); para una
  licencia OSI, usar un modelo como Mistral-Small-3.2 (Apache-2.0).
- Proveedor del endpoint (OVHcloud): contrato de encargado de tratamiento si se envían imágenes de personas
  reales (ver `docs/etica_y_normativa.md`).
- Evaluación de impacto antes de ampliar a otros contextos.

## Fases

1. **Piloto** (este reto): películas de dominio público, 1925–1968, con validación humana en 3 de ellas.
2. **Validación** con una institución usuaria y feedback; anotación independiente de una muestra mayor.
3. **Ampliación** a las 200 candidatas y, con acuerdos, a cine contemporáneo, series y televisión.

## Mantenimiento y sustitución de modelos

Los modelos se configuran en `config/config.yaml` y cada etapa es independiente: se puede sustituir
un modelo sin tocar el resto (sistema agnóstico respecto al modelo). Para vigilar la calidad, tras cada
cambio de modelo se vuelve a ejecutar `scripts/evaluate.py` sobre las anotaciones de `data/annotations/`.