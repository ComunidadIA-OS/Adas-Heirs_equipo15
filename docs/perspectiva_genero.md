# Perspectiva de género (10 % de la nota)

## Decisiones de diseño

- **Género percibido, no identidad.** El sistema no "sabe" el género de nadie; estima cómo lo
  percibiría un modelo entrenado con etiquetas humanas. Lo decimos en la demo y en los informes.
- **Categoría `no_determinado`.** Si el modelo no tiene mayoría clara (≥ 80 %) no se fuerza una etiqueta.
- **Binario como limitación explícita.** Los modelos disponibles solo predicen mujer/hombre.
  No lo presentamos como verdad, sino como limitación documentada.
- **Revisión humana.** La demo permite corregir etiquetas antes de publicar resultados.

## Evaluación de sesgos del clasificador

<!-- TODO: resultados sobre FairFace (CC BY 4.0) u otra muestra equilibrada:
precisión del género percibido por grupo de edad y tono de piel. ¿Falla más con algún grupo? -->

| Grupo | Precisión | Recall | Nº muestras |
|---|---|---|---|
| <!-- TODO --> | | | |

## Interpretación con perspectiva de género (lección de Karina Gibert)

Un dato puede leerse al revés si no se pone en contexto. Ejemplo: si en una película la protagonista
femenina tiene mucho tiempo en pantalla pero casi siempre en plano compartido y nunca sola, ¿es
protagonismo real o acompañamiento? Separad presencia (cuánto se las ve) de protagonismo (cómo se
las encuadra) antes de concluir.

Referente: el Geena Davis Institute (GD-IQ) midió que en las 200 películas más taquilleras de 2014–2015
los personajes masculinos tuvieron aproximadamente el doble de tiempo en pantalla que los femeninos.

<!-- TODO: comparar vuestros resultados por década con ese referente -->

## Referencias

- Formación "Perspectiva de género", Karina Gibert (14/10/2026)
- <!-- TODO: informe de sesgos de género en IA citado en la formación de ética -->
