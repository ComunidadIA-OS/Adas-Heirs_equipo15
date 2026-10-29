# Registro de decisiones y backlog

Apuntad aquí cada decisión importante (fecha, quién, por qué). Sirve para la presentación,
para la rendición de cuentas y para no repetir discusiones.

## Decisiones

| Fecha | Decisión | Por qué | Quién |
|---|---|---|---|
| 2026-10-24 | Modalidad: vídeo | Permite medir presencia y protagonismo visual (encuadre) con datos abiertos y es viable en el plazo; el audio queda en la hoja de ruta | Equipo |
| 2026-10-24 | Corpus: películas de dominio público (1925–1968) de Internet Archive | Licencia abierta declarada, comparación por épocas, tema de interés del equipo | Equipo |
| 2026-10-24 | 17 películas y no 200 | Representatividad: es un estudio exploratorio; coste de GPU; tiempo de anotación | Equipo |
| 2026-10-24 | Detector torchvision (BSD) en vez de YOLO Ultralytics (AGPL) | Compatibilidad con licencia MIT del repo | Equipo |
| 2026-10-24 | Votación por trayectoria con clase `no_determinado` | Un clasificador falla en frames sueltos | Equipo |
| 2026-10-26 | Detección de planos solo por brillo (`luma_only`, AdaptiveDetector) | Con color no detectaba ningún corte en películas en blanco y negro | Equipo |
| 2026-10-27 | Análisis de caras en GPU con onnxruntime-gpu 1.22.0 | La versión para CUDA 13 no soporta las V100S; por CPU tardaba ~3 h por película | Equipo |
| 2026-10-27 | Votación facial: umbral 70 % y mínimo 2 caras (antes 80 % y 3) | Análisis de sensibilidad con 6 películas: el tiempo sin determinar baja 6–11 puntos y el % de mujeres cambia menos de 2 puntos | Equipo |
| 2026-10-29 | Anotación humana propia como referencia de evaluación (3 películas, 94 personas) | No hay etiquetas de género percibido para cine antiguo; hay que medirlo en nuestro dominio | Judith y Kyara |
| 2026-10-29 | El análisis facial (InsightFace) falla en cine antiguo | Evaluación sobre *Detour* (25 personas anotadas): 0 de 4 mujeres detectadas y 10 de 25 personas sin decidir (40 %). Motivo para añadir una segunda opinión | Judith |
| 2026-10-29 | Añadir un modelo de visión como opinión principal del género percibido (etapa `vlm`), con la cara como respaldo | Con la cara: 0 de 4 mujeres en *Detour*; con el modelo de visión: 4 de 4 y 20 de 21 hombres | Equipo |
| 2026-10-29 | Modelo: Qwen2.5-VL-72B-Instruct (OVH AI Endpoints), 6 recortes por persona, umbral 60 %, mínimo 2 votos | Barrido de parámetros sobre 52 personas anotadas (*Detour* y *The General*): 46 aciertos, 2 errores, 4 sin decidir. Mistral-Small-3.2 (Apache-2.0) etiquetaba hombres como mujeres | Kyara y Judith |
| 2026-10-29 | Prioridad al modelo de visión sobre la cara, no al revés | Probado: la cara comete errores con alta confianza, el modelo de visión no | Equipo |
| 2026-10-29 | Parámetros congelados tras validar con una película nueva (*A Star Is Born*, color, 42 personas) | Los parámetros se eligieron con las dos primeras películas; hacía falta datos que no los hubieran influido | Judith |
| 2026-10-29 | *The General* deja de estar "dudosa" | Con la cara salía un 84 % de mujeres (error). Con el modelo de visión, 15,5 % de las personas y 18,3 % del tiempo, y la anotación humana lo confirma (4 de 6 mujeres, 18 de 21 hombres) | Kyara |
| 2026-10-29 | Se revisaron dos anotaciones de *A Star Is Born* tras compararlas con el sistema | Fueron errores de la anotadora; se declara que solo se revisaron los casos discrepantes (las cifras pueden ser algo optimistas) | Judith |
| 2026-10-29 | Se mantiene el índice de protagonismo sin reajustar pesos ni umbral, y se declara que es conservador | Acuerdo con el juicio humano: 62 de 94 (66 %); marca bien a quien marca (17 de 18) pero solo detecta 17 de 48 protagonistas. Ajustarlo con las mismas 94 personas sobreajustaría | Judith |

## Backlog (ideas para después, priorizadas)

- [ ] Audio: quién habla (Whisper + diarización) y cruzarlo con quién sale en plano
- [ ] Re-identificación de la misma persona en planos distintos
- [ ] Orientación de la cara (frontal/perfil) como componente del índice
- [ ] Medida de incertidumbre del % final (intervalos)
- [ ] Máscaras de segmentación para recortar a una sola persona (hoy dos cajas solapadas dan recortes con dos personas)
- [ ] Probar otros modelos de visión abiertos con licencia OSI (p. ej. Mistral-Small-3.2, Apache-2.0)
- [ ] Evaluar el sesgo por edad y tono de piel (p. ej. con FairFace)
- [ ] Segunda anotadora independiente en todas las películas y medir el acuerdo (kappa)