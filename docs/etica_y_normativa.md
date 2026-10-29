# Marco ético y cumplimiento normativo

## Los 7 principios del código ético europeo (Ethics Guidelines for Trustworthy AI)

| Principio | Cómo lo cumple el proyecto |
|---|---|
| Agencia y supervisión humanas | Demo con revisión: una persona acepta o corrige las etiquetas antes de usar el informe |
| Robustez técnica y seguridad | Evaluación con 94 personas anotadas a mano en 3 películas; votación por trayectoria con mayoría mínima; `no_determinado` cuando no hay evidencia; reanudación de la etapa si falla la API |
| Privacidad y gobernanza de datos | No se guardan recortes ni caras ni embeddings; los recortes se envían al endpoint de OVHcloud solo para la consulta (el proveedor declara que no almacena los datos ni los usa para entrenar); solo se publican datos agregados; no se identifica a nadie |
| Transparencia | Métricas y pesos públicos y documentados; código abierto; se declara el uso de IA, los modelos y sus licencias; las cifras de error por género se publican |
| Diversidad, no discriminación y equidad | Evaluación de errores por género (en nuestra muestra, el sistema lee como hombres a algunas mujeres y no al revés: se declara); género percibido, no identidad. No se ha evaluado por edad ni tono de piel (limitación declarada) |
| Bienestar social y ambiental | Desarrollo en local con muestras pequeñas; GPU para el corpus; el modelo de visión es grande (72.000 millones de parámetros) pero se usa solo para recortes pequeños y de forma reanudable; el modelo es sustituible por uno más pequeño |
| Rendición de cuentas | Repositorio reproducible; registro de decisiones en `docs/decisiones.md`; el uso de asistentes de IA para escribir el código está declarado en el README |

## Reglamento Europeo de IA (en vigor desde el 1/08/2024)

Análisis del equipo (a contrastar con las mentoras en Discord):

- **No hay identificación biométrica**: no reconocemos quién es nadie, solo estimamos un atributo
  (género percibido) por persona seguida en un vídeo.
- **Prácticas prohibidas**: la categorización biométrica prohibida es la que infiere raza, opiniones
  políticas, afiliación sindical, creencias, vida u orientación sexual. El género percibido no está entre
  esos atributos y no se usa para tomar decisiones sobre personas.
- **Posible alto riesgo en un despliegue real**: el anexo III incluye la categorización biométrica por
  atributos protegidos. Si el sistema se usara para categorizar a personas reales, habría que tratarlo
  como de alto riesgo (evaluación de conformidad, gestión de riesgos, documentación y supervisión humana).
- **Este piloto**: se desarrolla con fines de investigación sobre obras audiovisuales históricas, con
  resultados estadísticos y agregados, sin decisiones sobre personas concretas. Para un despliegue
  comercial se haría consulta jurídica previa y se aplicaría el régimen de alto riesgo.
- **Salvaguardas ya aplicadas**: supervisión humana en la demo, `no_determinado`, publicación de las
  tasas de error por género, documentación del uso previsto y de los límites, código abierto.

## RGPD

- **Datos tratados**: imágenes de personas que aparecen en películas publicadas entre 1925 y 1968.
  La mayoría de las personas que actúan en ellas han fallecido (el RGPD solo protege a personas vivas);
  puede haber figurantes vivos o con descendientes.
- **Base jurídica** (si se trataran datos de personas vivas): interés público y fines de investigación
  científica o histórica (art. 6.1.e y art. 89), con las salvaguardas del art. 89.1.
- **Minimización**: no se almacenan recortes, caras ni identidades; solo se conserva por persona seguida
  la etiqueta de género percibido, su confianza y las métricas agregadas.
- **Envío al proveedor**: los recortes (imágenes pequeñas de una persona) se envían a OVHcloud AI
  Endpoints, un proveedor europeo, solo para obtener la respuesta. OVHcloud declara que el servicio no
  almacena los datos del usuario ni los usa para entrenar sus modelos. En un uso con personas reales
  habría que firmar el contrato de encargado de tratamiento y comprobar la ubicación del servicio.
- **Figuras públicas**: los actores y actrices son figuras públicas en obras publicadas; no se identifica
  a nadie ni se publican imágenes.

## Datos de terceros

Películas con licencia abierta declarada en Internet Archive (dominio público en EE. UU.). No se
redistribuyen los vídeos ni fragmentos; solo estadísticas agregadas. Los actores y actrices son figuras
públicas en obras publicadas; no se identifica a nadie. Ver `datos_y_licencias.md`.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Etiquetado erróneo de género de una persona | `no_determinado`, revisión humana, solo resultados agregados, tasas de error publicadas |
| Sesgo del clasificador: en nuestra muestra solo se equivoca leyendo mujeres como hombres (4 de 39) | Se declara; las cifras de presencia de mujeres se leen como cota inferior; evaluar con más muestra |
| El modelo de visión se apoya en ropa o peinado (estereotipos) | Evaluación contra anotación humana; modelo sustituible; no se usa para decidir sobre personas |
| Sesgo del corpus (cine clásico estadounidense, repartos mayoritariamente blancos) | Presentado como estudio de caso exploratorio, no como "el cine" |
| Datos personales enviados a un tercero (recortes al endpoint) | Proveedor europeo que declara no almacenar ni reutilizar; sin identidades; recortes pequeños; en producción, contrato de tratamiento o modelo alojado propio |
| Uso del sistema para vigilar a personas concretas | Licencia y documentación de uso previsto; no se guarda identidad; el sistema no reconoce personas |
| Dependencia de un proveedor y de sus límites de uso | Modelo y `base_url` configurables; etapa reanudable; posibilidad de alojar un modelo propio |
| Interpretar mal un dato (presencia ≠ protagonismo) | Se separan las dos métricas y se explica en `docs/perspectiva_genero.md` |