# Perspectiva de género (10 % de la nota)

## Decisiones de diseño

- **Género percibido, no identidad.** El sistema no "sabe" el género de nadie; estima cómo lo
  percibiría un observador a partir del aspecto (cara, pelo, ropa, complexión). Lo decimos en la demo
  y en los informes.
- **Categoría `no_determinado`.** Si no hay mayoría clara no se fuerza una etiqueta. El modelo de visión
  decide cuando al menos 2 de sus respuestas coinciden y suponen un 60 % o más; si no, se usa el análisis
  facial como respaldo, y si tampoco decide queda como `no_determinado`.
- **Binario como limitación explícita.** Los modelos disponibles solo predicen mujer/hombre.
  No lo presentamos como verdad, sino como limitación documentada.
- **Riesgo de estereotipos.** Un modelo de visión puede apoyarse en la ropa o el peinado y no solo en
  rasgos físicos (en pruebas previas con otro modelo vimos hombres con pelo largo leídos como mujeres).
  Por eso medimos sus errores contra anotación humana y declaramos el sesgo que encontramos.
- **Modelo abierto e intercambiable.** El modelo de visión (Qwen2.5-VL-72B, OVH AI Endpoints) se cambia
  por otro desde `config/config.yaml`, sin tocar el código.
- **Revisión humana.** La demo permite corregir etiquetas antes de publicar resultados.

## Evaluación de sesgos del clasificador

| Grupo | Precisión | Recall | Sin decidir | Nº muestras |
|---|---|---|---|---|
| Detour (B/N, sonora): mujeres | 1,00 | 1,00 (4 de 4) | 0 de 4 (0 %) | 4 |
| Detour (B/N, sonora): hombres | 1,00 | 0,95 (20 de 21) | 1 de 21 (5 %) | 21 |
| The General (muda): mujeres | 1,00 | 0,67 (4 de 6) | 0 de 6 (0 %) | 6 |
| The General (muda): hombres | 0,90 | 0,86 (18 de 21) | 3 de 21 (14 %) | 21 |
| A Star Is Born (color): mujeres | 1,00 | 0,86 (25 de 29) | 2 de 29 (7 %) | 29 |
| A Star Is Born (color): hombres | 0,82 | 0,90 (9 de 10) | 1 de 10 (10 %) | 10 |
| **Total: mujeres** | 1,00 | 0,85 (33 de 39) | 2 de 39 (5 %) | 39 |
| **Total: hombres** | 0,92 | 0,90 (47 de 52) | 5 de 52 (10 %) | 52 |

Las tres películas suman 94 personas anotadas a mano (3 de ellas "no determinado", en las que el
sistema coincidió). El sistema acierta 83 (88 %), se equivoca en 4 (4 %) y deja 7 sin decidir.
Los 4 errores son mujeres percibidas como hombres; ningún hombre fue percibido como mujer, por lo
que el sistema tiende a infravalorar la presencia de mujeres (4 de 39, un 10 %). Las dos primeras
películas se usaron para elegir los parámetros del modelo de visión; A Star Is Born (color) no, y es
la medida más honesta. En A Star Is Born se revisaron dos anotaciones tras compararlas con el
sistema; el resto no se revisó, por lo que las cifras pueden ser algo optimistas. Los errores se
concentran en recortes con dos personas solapadas, figuras cortadas o muy pequeñas y planos
oscuros o de perfil. Las muestras son pequeñas (sobre todo de mujeres), así que las cifras son
orientativas.

No se ha evaluado el rendimiento por edad ni por tono de piel: las películas son históricas, en su mayoría en blanco y negro, y las anotaciones no recogen esas variables. Queda como limitación y trabajo futuro.

## Interpretación con perspectiva de género (lección de Karina Gibert)

Un dato puede leerse al revés si no se pone en contexto. Ejemplo: si en una película la protagonista
femenina tiene mucho tiempo en pantalla pero casi siempre en plano compartido y nunca sola, ¿es
protagonismo real o acompañamiento? Separamos presencia (cuánto se las ve) de protagonismo (cómo se
las encuadra) antes de concluir.

Referente: el Geena Davis Institute (GD-IQ) midió que en las 200 películas más taquilleras de 2014–2015
los personajes masculinos tuvieron aproximadamente el doble de tiempo en pantalla que los femeninos.

### Nuestros resultados frente a ese referente

Procesamos con el sistema final tres películas (el resto del corpus solo tiene el análisis facial
previo, que no es comparable, por lo que no se incluye). Son pocas para hablar de "por década":
cubren 1926–1945 y se presentan película a película.

| Película | Mujeres (% tiempo en pantalla) | Hombres (% tiempo en pantalla) | Hombres/mujeres |
|---|---|---|---|
| The General (1926, muda) | 18,3 % | 75,2 % | 4,1 veces |
| Detour (1945, B/N) | 30,7 % | 64,9 % | 2,1 veces |
| A Star Is Born (1937, color) | 31,1 % | 59,4 % | 1,9 veces |

(El resto, entre un 4,3 % y un 9,5 % según la película, es tiempo de personas con género no
determinado. El "tiempo en pantalla" es la suma de segundos de cada persona seguida, no la duración
de la película.)

Lectura:

- Detour (2,1 veces) y A Star Is Born (1,9 veces) están cerca del referente actual (hombres con
  unas 2 veces más tiempo que mujeres). The General queda muy por encima (más de 4 veces), coherente
  con una película de acción muda con un reparto casi masculino.
- Presencia y protagonismo no cuentan la misma historia. En Detour las mujeres suponen el 30,7 % del
  tiempo pero el 24,6 % de las personas marcadas como protagonistas, y su índice medio de protagonismo
  es algo menor que el de los hombres (0,26 frente a 0,28). En The General y en A Star Is Born ocurre
  lo contrario: aunque tienen menos tiempo (18,3 % y 31,1 %), concentran más protagonistas
  (21,2 % y 48,3 %) y un índice medio mayor (0,39 frente a 0,31 y 0,27 frente a 0,23). Las mujeres que
  aparecen suelen estar encuadradas de forma destacada, sobre todo en A Star Is Born, que tiene una
  protagonista femenina. Son solo tres películas, así que es una observación, no una conclusión general.
- Como el sistema lee a algunas mujeres como hombres (4 de 39 en la muestra anotada, un 10 %), el tiempo
  real de las mujeres es probablemente algo mayor que el medido.
- En A Star Is Born el 16 % de las personas seguidas queda como `no_determinado` (muchas son figuras
  pequeñas o cortadas en escenas oscuras), el mayor porcentaje de las tres. Es una incertidumbre
  que conviene tener presente al leer los porcentajes de personas.

## Referencias

- Formación "Perspectiva de género", Karina Gibert (14/10/2026)
- Geena Davis Institute on Gender in Media, estudio GD-IQ (2014–2015) sobre tiempo en pantalla.
- Buolamwini, J. y Gebru, T. (2018). *Gender Shades: Intersectional Accuracy Disparities in Commercial
  Gender Classification*. Proceedings of Machine Learning Research 81. Muestra que los clasificadores
  comerciales de género fallan más con mujeres, sobre todo las de piel más oscura.
- UNESCO (2019). *I'd blush if I could: closing gender divides in digital skills through education*.