# Datos y licencias

## Corpus principal: cine clásico de dominio público (Internet Archive)

- Fuente: colección *Feature Films* de Internet Archive — https://archive.org/details/feature_films
- Selección: **17 largometrajes de 1925 a 1968** en `data/sources.csv`, repartidos por décadas.
- Candidatas: `data/candidatas_200.csv` — 200 largometrajes con licencia abierta declarada
  (Public Domain, Public Domain Mark, CC0 o CC BY), ordenados por descargas. Reserva para escalar.

### Criterios de selección

1. Licencia abierta declarada y película estadounidense anterior a 1970 (licencia más fiable).
2. Distintas décadas (1920s–1960s) para poder comparar épocas.
3. Calidad de imagen suficiente para detectar caras; se incluyen varias en color.
4. Sin protagonistas menores de edad (los clasificadores fallan con niñas y niños).
5. Variedad de géneros (comedia, drama, cine negro, terror, western, musical) y de repartos,
   incluida *The Blood of Jesus* (1941), de cineasta y reparto afroamericanos.
6. Fuera: documentales, propaganda, animación y películas de explotación sexual o de drogas.

Cada película tiene su motivo en la columna `motivo_seleccion`. Antes de usarla, abrid su ficha,
comprobad la licencia y poned `licencia_verificada = si`.

### Qué significa "dominio público" aquí (importante)

- La licencia la **declara quien sube** la película a Internet Archive; no es una garantía.
- Casi siempre significa dominio público **en EE. UU.** (p. ej. copyright no renovado). En la UE una
  película está protegida hasta 70 años después de la muerte del último de sus autores principales
  (director, guionista, autor de diálogos, compositor), así que algunas podrían seguir protegidas aquí.
- Mitigación: **no redistribuimos los vídeos** (no están en el repo) ni fragmentos; solo publicamos
  estadísticas agregadas. Contrastar con las mentoras si el análisis está cubierto por las excepciones
  de minería de textos y datos (Directiva (UE) 2019/790).
- Atribución: columna `atribucion` (título, año y URL de Internet Archive).

### Limitaciones del corpus

- **No representa "el cine"**: es cine clásico estadounidense de dominio público, con mucha serie B y
  repartos mayoritariamente blancos. Los resultados se presentan como **estudio de caso exploratorio**.
- Blanco y negro y baja resolución en muchas películas: el modelo rinde peor (ver evaluación de sesgos).
- Contenido con estereotipos sexistas y racistas de época: se analiza (es parte del objetivo), pero se
  contextualiza y no se muestra en la demo sin explicación.

## Evaluación de sesgos: FairFace

- https://github.com/joojs/fairface — 108.501 imágenes de caras equilibradas por grupo, con género y
  edad. Licencia CC BY 4.0.
- **No se ha utilizado en este reto.** Evaluamos el género percibido directamente sobre nuestro dominio
  (cine antiguo, 94 personas anotadas a mano), porque un conjunto de fotos modernas no refleja la
  calidad del material. Queda como trabajo futuro para medir el sesgo por edad y tono de piel.

## Ground truth propio

`data/annotations/anotaciones.csv` — anotado a mano por el equipo (ver README de esa carpeta):
94 personas en 3 películas de épocas distintas (*The General*, muda, 1926; *A Star Is Born*, color, 1937;
*Detour*, blanco y negro sonoro, 1945). Se anota el género **percibido** y si la persona es protagonista del plano.

## Modelos de terceros usados en la evaluación del género

| Modelo | Uso | Licencia |
|---|---|---|
| Qwen2.5-VL-72B-Instruct (vía OVHcloud AI Endpoints) | Género percibido a partir de un recorte de la persona | Licencia propia de Qwen: pesos abiertos, **no es OSI**; permite uso comercial con condiciones |
| Mistral-Small-3.2-24B-Instruct (probado, no elegido) | Alternativa evaluada | Apache-2.0 |
| InsightFace (modelos `buffalo_l`) | Respaldo facial | Uso **no comercial** |

El modelo de visión es sustituible por cualquiera compatible con la API de OpenAI (`vlm.model` en
`config/config.yaml`). Los recortes que se envían a la API no se guardan en el repositorio.
