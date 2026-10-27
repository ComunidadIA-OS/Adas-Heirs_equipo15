"""Crea un vídeo corto con las personas seguidas dibujadas, para poder anotar a mano.

Cada persona sale con una caja de color y su número de trayectoria (track_id) en grande.
Así se sabe qué fila de anotaciones.csv corresponde a cada persona.

Además crea una plantilla de anotaciones con una fila por persona que aparece en el trozo,
con la columna de género VACÍA: la rellenáis vosotras sin mirar lo que dijo el programa
(si lo veis antes, os influye y la evaluación ya no vale).

Uso (después de procesar la película con src.pipeline):
  python scripts/dibujar_trayectorias.py --video /workspace/videos/Detour.mp4 --desde 60 --hasta 240

Salida:
  outputs/<película>/revision_<desde>-<hasta>.mp4        vídeo con las cajas
  outputs/<película>/plantilla_<desde>-<hasta>.csv       filas para copiar a anotaciones.csv

Además crea dos imágenes para anotar sin tener que ver todo el vídeo:
  outputs/<película>/fichas_personas_<desde>-<hasta>.png   una miniatura por persona (su caja, número y minuto)
  outputs/<película>/fichas_planos_<desde>-<hasta>.png     una imagen por plano con todas las cajas

Opcional: --mostrar-etiqueta escribe también lo que dijo el programa (solo para revisar, NO para anotar).
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COLORES = [(66, 135, 245), (245, 130, 48), (60, 180, 75), (230, 25, 75), (145, 30, 180),
           (70, 240, 240), (240, 50, 230), (210, 245, 60), (0, 128, 128), (170, 110, 40)]


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    return datos


def color_de(track_id):
    return COLORES[track_id % len(COLORES)]


def dibujar(frame, observaciones, etiquetas, mostrar_etiqueta):
    for o in observaciones:
        x1, y1, x2, y2 = [int(v) for v in o["box"]]
        color = color_de(o["track_id"])
        texto = str(o["track_id"])
        if mostrar_etiqueta:
            texto = f"{texto} {etiquetas.get(o['track_id'], '?')}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        (ancho, alto), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        y_texto = max(alto + 8, y1)
        x_texto = max(0, min(x1, frame.shape[1] - ancho - 8))   # que no se salga por la derecha
        cv2.rectangle(frame, (x_texto, y_texto - alto - 8), (x_texto + ancho + 8, y_texto), color, -1)
        cv2.putText(frame, texto, (x_texto + 4, y_texto - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (255, 255, 255), 2, cv2.LINE_AA)
    return frame


def minuto(segundo):
    return f"{int(segundo // 60):02d}:{segundo % 60:04.1f}"


def leer_frame(cap, idx):
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    resultado = None
    if ok:
        resultado = frame
    return resultado


def rotular(imagen, texto):
    """Añade una franja negra abajo con el texto."""
    alto, ancho = imagen.shape[:2]
    franja = np.zeros((34, ancho, 3), dtype=np.uint8)
    cv2.putText(franja, texto, (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    return np.vstack([imagen, franja])


def mosaico(imagenes, columnas, ancho_celda):
    """Pone las imágenes en una cuadrícula, todas con el mismo ancho."""
    filas_img = []
    celdas = []
    for im in imagenes:
        escala = ancho_celda / im.shape[1]
        celdas.append(cv2.resize(im, (ancho_celda, int(im.shape[0] * escala))))
    alto_celda = max(c.shape[0] for c in celdas)
    celdas = [cv2.copyMakeBorder(c, 0, alto_celda - c.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(40, 40, 40))
              for c in celdas]
    vacia = np.full((alto_celda, ancho_celda, 3), 40, dtype=np.uint8)
    while len(celdas) % columnas:
        celdas.append(vacia)
    for i in range(0, len(celdas), columnas):
        fila = [cv2.copyMakeBorder(c, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255, 255, 255))
                for c in celdas[i:i + columnas]]
        filas_img.append(np.hstack(fila))
    return np.vstack(filas_img)


def fichas_personas(cap, fps, por_track, ruta):
    """Una miniatura por persona: el fotograma central de su trayectoria, con su caja."""
    imagenes = []
    for tid in sorted(por_track):
        obs = por_track[tid]
        o = obs[len(obs) // 2]
        frame = leer_frame(cap, o["frame"])
        if frame is not None:
            x1, y1, x2, y2 = [int(v) for v in o["box"]]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            imagenes.append(rotular(frame, f"{tid}  ({minuto(o['frame'] / fps)})"))
    if imagenes:
        cv2.imwrite(str(ruta), mosaico(imagenes, 3, 420))
    return len(imagenes)


def fichas_planos(cap, fps, planos, por_frame, primero, ultimo, paso, ruta):
    """Una imagen por plano (su fotograma analizado central) con todas sus cajas."""
    imagenes = []
    for pl in planos:
        ini = max(primero, int(pl["start_s"] * fps))
        fin = min(ultimo, int(pl["end_s"] * fps))
        if fin > ini:
            centro = (ini + fin) // 2
            centro = centro - centro % paso          # fotograma que el programa analizó
            frame = leer_frame(cap, centro)
            if frame is not None:
                dibujar(frame, por_frame.get(centro, []), {}, False)
                imagenes.append(rotular(frame, f"plano {pl['shot_id']}  {minuto(ini / fps)} - {minuto(fin / fps)}"))
    if imagenes:
        cv2.imwrite(str(ruta), mosaico(imagenes, 3, 420))
    return len(imagenes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--desde", type=float, default=0.0, help="segundo de inicio")
    ap.add_argument("--hasta", type=float, default=180.0, help="segundo final")
    ap.add_argument("--outputs", default=str(ROOT / "outputs"))
    ap.add_argument("--mostrar-etiqueta", action="store_true")
    args = ap.parse_args()

    video = Path(args.video)
    carpeta = Path(args.outputs) / video.stem
    tracks = leer_json(carpeta / "tracks.json")
    etiquetas = {}
    if (carpeta / "personas.json").exists():
        etiquetas = {p["track_id"]: p["label"] for p in leer_json(carpeta / "personas.json")["personas"]}

    # Observaciones agrupadas por fotograma analizado
    por_frame = defaultdict(list)
    for o in tracks["observations"]:
        por_frame[o["frame"]].append(o)

    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    primero = int(args.desde * fps)
    ultimo = int(args.hasta * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, primero)

    nombre = f"{int(args.desde)}-{int(args.hasta)}"
    salida = carpeta / f"revision_{nombre}.mp4"
    escritor = cv2.VideoWriter(str(salida), cv2.VideoWriter_fourcc(*"mp4v"), fps, (ancho, alto))

    # El pipeline analiza 1 de cada 'paso' fotogramas (fps_sample por segundo). Entre dos fotogramas
    # analizados se mantienen las cajas del último analizado; si en él no había nadie, no se dibuja nada.
    paso = max(1, round(fps / tracks["fps_sample"]))
    ultimas = []
    vistos = defaultdict(int)
    idx = primero
    seguir = True
    while seguir:
        ok, frame = cap.read()
        if ok and idx <= ultimo:
            if idx % paso == 0:
                ultimas = por_frame.get(idx, [])
                for o in ultimas:
                    vistos[o["track_id"]] += 1
            segundo = idx / fps
            cv2.putText(frame, f"{int(segundo // 60):02d}:{segundo % 60:04.1f}", (10, alto - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            escritor.write(dibujar(frame, ultimas, etiquetas, args.mostrar_etiqueta))
            idx += 1
        else:
            seguir = False
    cap.release()
    escritor.release()

    plantilla = carpeta / f"plantilla_{nombre}.csv"
    with open(plantilla, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["video_id", "track_id", "genero_percibido", "protagonista", "notas"])
        for tid in sorted(vistos):
            w.writerow([video.stem, tid, "", "", f"sale en {vistos[tid]} imágenes analizadas"])

    por_track = defaultdict(list)
    for o in tracks["observations"]:
        if primero <= o["frame"] <= ultimo:
            por_track[o["track_id"]].append(o)
    planos = leer_json(carpeta / "planos.json")["shots"]
    cap = cv2.VideoCapture(str(video))
    n_p = fichas_personas(cap, fps, por_track, carpeta / f"fichas_personas_{nombre}.png")
    n_s = fichas_planos(cap, fps, planos, por_frame, primero, ultimo, paso, carpeta / f"fichas_planos_{nombre}.png")
    cap.release()

    print(f"Vídeo: {salida}")
    print(f"Fichas: {n_p} personas en fichas_personas_{nombre}.png, {n_s} planos en fichas_planos_{nombre}.png")
    print(f"Plantilla con {len(vistos)} personas: {plantilla}")
    print("Rellenad genero_percibido (mujer/hombre/no_determinado) y protagonista (si/no)")
    print("y copiad las filas a data/annotations/anotaciones.csv")


if __name__ == "__main__":
    main()
