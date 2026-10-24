# Registro de decisiones y backlog

Apuntad aquí cada decisión importante (fecha, quién, por qué). Sirve para la presentación,
para la rendición de cuentas y para no repetir discusiones.

## Decisiones

| Fecha | Decisión | Por qué | Quién |
|---|---|---|---|
| 2026-10-24 | Modalidad: vídeo | <!-- TODO --> | Equipo |
| 2026-10-24 | Corpus: 17 películas de dominio público (1925–1968) de Internet Archive | Licencia abierta declarada, comparación por épocas, tema de interés del equipo | Equipo |
| 2026-10-24 | 17 películas y no 200 | Representatividad: es un estudio exploratorio; coste de GPU; tiempo de anotación | Equipo |
| 2026-10-24 | Detector torchvision (BSD) en vez de YOLO Ultralytics (AGPL) | Compatibilidad con licencia MIT del repo | Equipo |
| 2026-10-24 | Votación por trayectoria con umbral 80 % y clase `no_determinado` | El clasificador falla en frames sueltos | Equipo |

## Backlog (ideas para después, priorizadas)

- [ ] Audio: quién habla (Whisper + diarización) y cruzarlo con quién sale en plano
- [ ] Re-identificación de la misma persona en planos distintos
- [ ] Orientación de la cara (frontal/perfil) como componente del índice
- [ ] Medida de incertidumbre del % final (intervalos)
- [ ] <!-- TODO -->
