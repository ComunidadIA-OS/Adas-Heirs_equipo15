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
- Procesamiento: GPU (piloto en OVHcloud, 2× V100S). <!-- TODO: tiempo por hora de vídeo medido -->
- Coste estimado: <!-- TODO: horas de GPU por hora de vídeo × precio; mantenimiento -->

## Permisos y acuerdos necesarios

- Películas de dominio público: comprobar la licencia de cada una (y su estado en la UE).
- Archivo de filmotecas o catálogos comerciales: **acuerdo previo** con el titular de los derechos.
- Televisiones: **acuerdo previo** con la cadena para acceder a su archivo mediante API; nunca scraping.
- Modelos de terceros: revisar licencias (InsightFace = uso no comercial → para uso comercial
  sustituir por un modelo con licencia compatible).
- Evaluación de impacto antes de ampliar a otros contextos.

## Fases

1. **Piloto** (este reto): 17 películas de dominio público, 1925–1968.
2. **Validación** con una institución usuaria y feedback.
3. **Ampliación** a las 200 candidatas y, con acuerdos, a cine contemporáneo, series y televisión.

## Mantenimiento y sustitución de modelos

Los modelos se configuran en `config/config.yaml` y cada etapa es independiente: se puede sustituir
un modelo sin tocar el resto (sistema agnóstico respecto al modelo).
