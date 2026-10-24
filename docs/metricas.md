# Propuesta de métricas (entregable 1)

> Este documento es la "propuesta conceptual de métricas" que pide el reto.
> Rellenad los TODO y justificad cada decisión: la justificación es parte de la nota.

## Problema reformulado (una frase)

<!-- TODO -->

## Qué entendemos por protagonismo en vídeo

<!-- TODO: definición del equipo. Ej: "Una persona es protagonista cuando la realización del vídeo
la sitúa en el centro de la atención visual: aparece mucho tiempo, en grande, centrada, sola en plano
y en los momentos de apertura o cierre." -->

## Nivel 1 — Presencia

| Métrica | Definición | Por qué |
|---|---|---|
| % personas | personas distintas de cada género percibido / total | Cuántas mujeres aparecen |
| % tiempo en pantalla | segundos en pantalla por género / total | Cuánto se las ve |

## Nivel 2 — Protagonismo (por persona)

| Componente | Cálculo | Peso | Justificación |
|---|---|---|---|
| Tiempo en pantalla | segundos / máx. del vídeo | 0.30 | <!-- TODO --> |
| Tamaño | área media de la caja / área del frame, normalizada | 0.20 | Primer plano = más atención |
| Centralidad | 1 − distancia al centro / distancia máxima | 0.15 | Pregunta del propio reto: ¿el centro es protagonista? |
| En solitario | % de frames en que es la única persona | 0.20 | Plano individual = foco de la realización |
| Apertura/cierre | aparece en el primer o último 10 % | 0.15 | El README del reto lo cita como indicador |

**Índice de protagonismo** = media ponderada (0–1). Persona protagonista si índice ≥ 0.5.
Los pesos están en `config/config.yaml`.

## Validación de las métricas

- ¿El índice coincide con el juicio humano? Comparar con la columna `protagonista` de las anotaciones.
- Análisis de sensibilidad: ¿cambian las conclusiones si cambiamos los pesos? <!-- TODO -->

## Limitaciones conocidas

- Género **percibido** por un modelo, binario; categoría `no_determinado` cuando hay duda.
- La centralidad depende de cómo graba cada institución o cadena.
- Sin audio no sabemos quién habla: alguien puede estar en plano sin intervenir.
- <!-- TODO -->
