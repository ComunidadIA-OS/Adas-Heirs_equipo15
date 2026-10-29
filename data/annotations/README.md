# Anotaciones manuales (ground truth)

Sirven para **evaluar** el sistema contra un juicio humano. Hoy contienen **94 personas en 3 películas** de
épocas distintas: *The General* (muda, 1926), *A Star Is Born* (color, 1937) y *Detour* (blanco y negro
sonoro, 1945).

## Qué contiene `anotaciones.csv`

| columna | valores |
|---|---|
| `video_id` | nombre del vídeo sin `.mp4` |
| `track_id` | ID de la trayectoria (persona seguida en un plano) |
| `genero_percibido` | `mujer` / `hombre` / `no_determinado` |
| `protagonista` | `si` / `no` (juicio humano) |
| `notas` | lo que se quiera (p. ej. "de perfil todo el rato") |

El género anotado es el **percibido**, igual que el del modelo. Si hay duda, `no_determinado`. No se guardan
nombres de personas.

## Cómo se anotó

1. Se procesa la película y se generan, con `scripts/dibujar_trayectorias.py`, un vídeo de revisión y las
   imágenes `outputs/<película>/fichas_*.png`, junto con una plantilla `outputs/<película>/plantilla_*.csv`.
2. Se rellenan en la plantilla las columnas `genero_percibido` y `protagonista` de cada persona.
3. Se añaden al CSV con:
   `python scripts/anadir_anotaciones.py outputs/<película>/plantilla_*.csv`
   (no duplica filas ya anotadas y guarda una copia `.bak`).
4. Se evalúa el género con `python scripts/evaluate.py` y el protagonismo con
   `python scripts/protagonismo_vs_humano.py`.

## Limitaciones

- Cada tramo de película lo ha anotado una sola persona, así que no se puede medir el acuerdo entre
  anotadoras. Queda como trabajo futuro anotar un mismo tramo entre dos personas y calcular el acuerdo (kappa).
- En *A Star Is Born* se revisaron dos anotaciones tras compararlas con el sistema; el resto no se revisó, por
  lo que las cifras pueden ser algo optimistas.
- Solo se anotó una parte de cada película (varios minutos), no la película entera.