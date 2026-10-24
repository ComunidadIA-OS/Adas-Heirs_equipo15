# Marco ético y cumplimiento normativo

## Los 7 principios del código ético europeo (Ethics Guidelines for Trustworthy AI)

| Principio | Cómo lo cumple el proyecto |
|---|---|
| Agencia y supervisión humanas | Demo con revisión: una persona acepta o corrige las etiquetas antes de usar el informe |
| Robustez técnica y seguridad | Evaluación con anotaciones manuales; votación por trayectoria; `no_determinado` |
| Privacidad y gobernanza de datos | No se guardan recortes de caras ni embeddings; solo datos agregados; no se identifica a nadie |
| Transparencia | Métricas y pesos públicos y documentados; código abierto; se declara el uso de IA |
| Diversidad, no discriminación y equidad | Evaluación de sesgos por edad/tono de piel; género percibido, no identidad |
| Bienestar social y ambiental | Desarrollo en local con muestras pequeñas; GPU solo para el corpus; modelos ligeros, sin IA generativa innecesaria |
| Rendición de cuentas | Repositorio reproducible; registro de decisiones en `docs/decisiones.md` |

## Reglamento Europeo de IA (en vigor desde el 1/08/2024)

<!-- TODO: clasificación de riesgo razonada del sistema. Puntos a analizar:
- No hay identificación biométrica de personas (no reconocemos QUIÉN es nadie).
- Sí hay inferencia de un atributo (género percibido) a partir de la cara: argumentad por qué
  no entra en las prácticas prohibidas y qué salvaguardas aplicamos.
- Uso estadístico/agregado, no para tomar decisiones sobre personas concretas.
Contrastad este análisis con las mentoras en Discord antes de entregarlo. -->

## RGPD

<!-- TODO: base jurídica (interés público / investigación), minimización, no conservación de
imágenes faciales, figuras públicas en actos públicos. -->

## Datos de terceros

Películas con licencia abierta declarada en Internet Archive (dominio público en EE. UU.). No se
redistribuyen los vídeos ni fragmentos; solo estadísticas agregadas. Los actores y actrices son figuras
públicas en obras publicadas; no se identifica a nadie. Ver `datos_y_licencias.md`.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Etiquetado erróneo de género de una persona | `no_determinado`, revisión humana, solo resultados agregados |
| Sesgo del clasificador con ciertos grupos | Evaluación por grupos y reporte de la limitación |
| Uso del sistema para vigilar a personas concretas | Licencia y documentación de uso previsto; no se guarda identidad |
| <!-- TODO --> | |
