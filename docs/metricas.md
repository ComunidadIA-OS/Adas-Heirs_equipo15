# Propuesta de métricas (entregable 1)
> Este documento es la "propuesta conceptual de métricas"

## Problema reformulado (una frase)

Medir, en vídeo, cuánto aparecen las mujeres y qué papel ocupan frente a la cámara, de forma
transparente y reproducible, sin asumir su identidad: solo el género que percibiría un observador.

## Qué entendemos por protagonismo en vídeo

Una persona es protagonista de un plano cuando la realización la sitúa en el centro de la atención
visual: se la ve en grande, de forma destacada en el encuadre, sola o claramente por encima de
quienes la rodean, y se mantiene en pantalla de forma sostenida. Distinguimos "protagonista" de
"presencia": una persona puede aparecer mucho tiempo y ser fondo, y otra puede aparecer poco y ser
el foco del plano.

No asumimos que la persona del centro sea siempre la protagonista:
la centralidad es solo uno de los cinco componentes y pesa poco (0,15).

## Nivel 1 — Presencia

| Métrica | Definición | Por qué |
|---|---|---|
| % personas | personas distintas de cada género percibido / total | Cuántas mujeres aparecen |
| % tiempo en pantalla | segundos en pantalla por género / total | Cuánto se las ve |

El tiempo en pantalla es la suma de los segundos de cada persona seguida, no la duración de la película.
Es más robusto que el recuento de personas, porque el sistema también sigue figuras muy pequeñas o muy cortas.

## Nivel 2 — Protagonismo (por persona)

| Componente | Cálculo | Peso | Justificación |
|---|---|---|---|
| Tiempo en pantalla | segundos / máx. de la película | 0.30 | El componente más objetivo y el menos sensible a cómo grabe cada película; quien más aparece suele ser el eje de la escena |
| Tamaño | área media de la caja / área del frame, normalizada | 0.20 | Primer plano = más atención |
| Centralidad | 1 − distancia al centro / distancia máxima | 0.15 | Pregunta del propio reto: ¿el centro es protagonista? Pesa menos porque depende de cómo encuadre cada director |
| En solitario | % de frames en que es la única persona | 0.20 | Plano individual = foco de la realización |
| Apertura/cierre | aparece en el primer o último 10 % | 0.15 | El README del reto lo cita como indicador. [CONFIRMAR: decidir si se mantiene o se justifica mejor] |

**Índice de protagonismo** = media ponderada (0–1). Persona protagonista si índice ≥ 0.5.
Los pesos están en `config/config.yaml`. Se fijaron a priori, por criterio del equipo, y no se han
entrenado: con pocas anotaciones, ajustarlos a ellas habría sobreajustado el índice.

## Validación de las métricas

- **Género percibido:** se mide contra anotación humana (94 personas, 3 películas); ver
  [`perspectiva_genero.md`](perspectiva_genero.md).
- **Protagonismo:** se compara la etiqueta "protagonista" del índice (umbral 0,5) con el juicio humano en las 3 películas (94 personas): coinciden en 62 (66 %). Por película: *Detour* 20 de 25 (80 %), *The General* 17 de 27 (63 %), *A Star Is Born* 25 de 42 (60 %). El índice es conservador: cuando marca a alguien como protagonista coincidimos casi siempre (17 de 18, 94 %), pero solo marca 17 de las 48 personas que nosotras consideramos protagonistas (35 %). 31 de los 32 desacuerdos son de este tipo y unos once tienen un índice entre 0,40 y 0,49, cerca del umbral. Los pesos y el umbral se fijaron antes de anotar y no se han ajustado a estas anotaciones, porque hacerlo sobre las mismas 94 personas sobreajustaría el índice. Dos posibles causas, sin comprobar: nuestra anotación juzga a cada persona dentro del tramo que vimos, mientras que el índice normaliza el tiempo en pantalla con el máximo de toda la película; y nuestro criterio de protagonista puede ser más generoso que el del índice.
- **Análisis de sensibilidad:** probamos variantes del índice (sin el componente de apertura/cierre y una
  variante con composición y primer plano propuesta por Luna). La variante de Luna sube el acuerdo a un
  84 % en *Detour*; con tan pocas anotaciones la diferencia no es concluyente, por lo que mantenemos
  el índice original.
- **Error típico del índice:** no marcar como protagonista a personas que sí lo parecen (por ejemplo, planos medios de personajes importantes con poco tiempo en pantalla). Por eso los porcentajes de protagonistas deben leerse como una cota inferior.

## Limitaciones conocidas

- Género **percibido** por un modelo de visión (con la cara como respaldo), binario; categoría
  `no_determinado` cuando hay duda. En nuestra muestra los errores son mujeres leídas como hombres (4 de 39).
- La centralidad depende de cómo graba cada institución o cadena.
- Sin audio no sabemos quién habla: alguien puede estar en plano sin intervenir.
- El protagonismo se mide por cómo trata la cámara a la persona, no por el guion: un personaje central que
  sale poco o cortado puede quedar infravalorado.
- La muestra anotada para validar es pequeña (decenas de personas) y los ajustes del modelo de visión se
  eligieron sobre parte de ella; por eso se contrastó con una película nueva.
- Los porcentajes se calculan sobre "personas seguidas" por el sistema, que incluye figuras pequeñas o
  muy cortas; el tiempo en pantalla es una medida más robusta que el recuento.