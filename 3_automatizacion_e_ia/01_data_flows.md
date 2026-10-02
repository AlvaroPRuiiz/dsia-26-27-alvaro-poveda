# Sesión 5 oct 2026 — Flujos de datos (data flows)

Ejercicio 30 min: `ejercicios/E4_pipeline.md`  
Demo: `ejemplos/pipeline_ventas.py`

## Mensaje de la exposición (30 min)

Un **data flow** de producto no es un notebook lineal: es un job **reproducible, observable y con contratos**.

```text
Ingesta → Validación → Transformación → Persistencia → Observabilidad
         (I/O)        (puro / testeable)   (I/O)         (logs+metrics)
```

### Propiedades

| Propiedad | Pregunta de diseño |
| --- | --- |
| Reproducibilidad | ¿Mismos inputs ⇒ mismos outputs? |
| Idempotencia | ¿Re-ejecutar es seguro? |
| Observabilidad | ¿Sé cuántas filas caí y por qué? |
| Fail-fast | ¿Prefiero abortar a publicar basura? |

### Live demo

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5
```

Inspecciona `metrics.json` y el log. Luego fuerza un umbral bajo (`0.05`) y observa el exit code.

### Separación I/O vs lógica

- `transform(df) -> (clean, report)` debe poder testearse **sin disco**.
- `load` / `save` son bordes: ahí viven path, permisos, encoding.

## Después de la teoría

Cronometra `E4_pipeline.md` (30 min) y sigue con Proyecto II.
