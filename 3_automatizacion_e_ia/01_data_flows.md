# Sesión 5 oct 2026 — Flujos de datos (data flows)

| Recurso | Fichero |
| --- | --- |
| Demo | [`ejemplos/pipeline_ventas.py`](ejemplos/pipeline_ventas.py) |
| Ejercicio de clase | [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) |
| Datos | [`Datos/ventas.csv`](Datos/ventas.csv) |
| Base previa (arquitectura) | [`../1_programacion_avanzada_python/03_arquitectura_patrones.md`](../1_programacion_avanzada_python/03_arquitectura_patrones.md) |

Este documento es la **referencia amplia** de data flows en DSIA: por qué un pipeline no es un notebook, los **tres conceptos clave** que debes dominar al salir de clase, y material suplementario (propiedades, exit codes, anti-patrones, puente al Proyecto II) para automatizar con criterio.

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar la sesión **debes** ser capaz de:

1. Describir un **data flow** por etapas: ingesta → validación/transformación → persistencia → observabilidad.
2. Separar **I/O** (load/save) de la **lógica pura** (`transform`) testeable sin disco.
3. Aplicar un **gate de calidad** (`max-error-rate` + logs + `metrics.json` + exit codes).

### Deseables (material suplementario)

4. Nombrar reproducibilidad, idempotencia, observabilidad y fail-fast.
5. Extender el demo con contrato de columnas y log a fichero (E4).
6. Escribir un test unitario de `transform()` con DataFrame en memoria.
7. Enlazar el pipeline con el dominio del **Proyecto II**.

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos

En DSIA no entregamos “un notebook que limpia ventas si pulso Run All”. Entregamos un **job** que otra persona (o CI/cron) pueda lanzar:

```bash
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir Datos/salida
```

y obtener artefactos + evidencia de calidad.

### 1.2 Mapa mental del semestre

```text
Tema 1  →  pandas + arquitectura (etapas y módulos)
Tema 2  →  pytest + CI (confianza)
Tema 3  →  data flows (hoy) + APIs IA     ← automatizas el núcleo
Tema 5  →  E2E / deploy                    ← el mismo flujo crece
```

El Proyecto II **parte** de un pipeline como este (datos → limpieza → métricas → más adelante IA + tests).

### 1.3 Analogías útiles

| Concepto | Analogía |
| --- | --- |
| Data flow / pipeline | Cadena de montaje con controles de calidad |
| Ingesta (`load`) | Recepción de materia prima |
| `transform` puro | Máquina que procesa sin salir de la nave |
| Persistencia (`save`) | Almacén de producto terminado |
| `metrics.json` | Parte de producción del turno |
| `run.log` | Cámara / libro de incidencias |
| `max-error-rate` | “Si hay >X % defectuoso, paramos la línea” |
| Exit code ≠ 0 | Alarma roja para CI o el operador |

### 1.4 Regla de oro

> **I/O en los bordes; reglas de negocio en el centro; si la calidad no llega, no publiques.**

---

# PARTE A — Tres conceptos clave (obligatorio)

> Prioridad de clase: A1 → A2 → A3. El resto es profundidad.

---

## A1. Concepto clave 1 — Etapas de un data flow

### Qué es

Un **data flow de producto** no es un notebook lineal: es un job **reproducible, observable y con contratos**.

```text
Ingesta → Validación → Transformación → Persistencia → Observabilidad
         (I/O)        (puro / testeable)   (I/O)         (logs + metrics)
```

| Etapa | Responsabilidad | En el demo |
| --- | --- | --- |
| Ingesta | Leer origen, comprobar existencia/esquema | `load()` |
| Validación / transform | Reglas de negocio, filas OK vs KO | `transform()` |
| Persistencia | Escribir salidas | `save()` |
| Observabilidad | Logs + métricas + códigos de salida | `setup_logging`, `report`, `main` return |

### Demo mínima

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5
```

Inspecciona:

- `Datos/salida/ventas_limpias.csv`
- `Datos/salida/metrics.json`
- `Datos/salida/run.log` (si el ejercicio lo exige / tras E4)

### Checklist del concepto 1

- [ ] Sé dibujar las 5 etapas en una frase cada una
- [ ] Sé lanzar el demo y apuntar a sus artefactos
- [ ] Sé explicar por qué esto no es un notebook de exploración

---

## A2. Concepto clave 2 — Separar I/O de lógica pura

### Qué es

| Capa | Puede tocar disco/red | Debe ser fácil de testear |
| --- | --- | --- |
| `load` / `save` | Sí | Con `tmp_path` o mocks |
| `transform(df) -> (clean, report)` | **No** (idealmente) | Con DataFrame en memoria |

Firma del demo:

```python
def transform(frame: pd.DataFrame, logger=None) -> tuple[pd.DataFrame, dict]:
    ...
```

### Por qué importa

- Unitario rápido: sin CSV, sin permisos, sin cwd frágil.
- Puedes cambiar CSV → JSON → API **sin** reescribir las reglas.
- Encaja con SOLID/Repository de la sesión de arquitectura.

### Test mínimo (idea)

```python
def test_transform_report_counts():
    df = pd.DataFrame({
        "unidades": [1, None, 2],
        "precio_unitario": [10.0, 5.0, -1.0],
        # ... resto de columnas si hace falta
    })
    clean, report = transform(df)
    assert report["rows_in"] == 3
    assert report["rows_dropped"] >= 1
```

### Checklist del concepto 2

- [ ] Sé señalar qué funciones son borde vs centro en el demo
- [ ] Sé decir por qué `transform` no debería hacer `to_csv` por dentro
- [ ] Sé esbozar un test sin tocar `Datos/`

---

## A3. Concepto clave 3 — Gate de calidad (fail-fast + observabilidad)

### Qué es

Antes de **publicar** (guardar limpio), decides si la corrida es aceptable.

En el demo:

```python
if report["error_rate"] > args.max_error_rate:
    logger.error("... abortando")
    return 1  # fallo controlado
```

| Señal | Significado |
| --- | --- |
| Exit `0` | OK: artefactos escritos |
| Exit `1` | Calidad insuficiente (umbral) |
| Exit `2` | Input inválido (path / columnas) — tras E4 |

### Práctica en aula

```bash
# Debe fallar con el CSV del curso (10/150 ≈ 0.067 > 0.05)
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out \
  --max-error-rate 0.05
echo $?   # 1
```

Con umbral holgado (`0.5`) → exit `0` y `metrics.json` con `error_rate`.

### Observabilidad mínima

1. **Log** — qué pasó (info/error).  
2. **Métricas** — conteos (`rows_in`, `rows_out`, `rows_dropped`, `error_rate`, …).  
3. **Exit code** — para humanos, scripts y CI.

### Checklist del concepto 3

- [ ] Sé calcular mentalmente `error_rate = dropped / rows_in`
- [ ] Sé forzar un rojo con `--max-error-rate 0.05`
- [ ] Sé leer `metrics.json` y relacionarlo con el abort

---

## A4. Mapa mental de los 3 conceptos

```text
Etapas del flow     →  qué hace el job, en orden
I/O vs transform    →  qué se testea barato
Gate de calidad     →  cuándo está permitido publicar
```

**Siguiente paso inmediato en clase:** [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md).

---

# PARTE B — Material suplementario

> Úsalo para profundizar y para el Proyecto II. **No** sustituye a A1–A3.

---

## B1. Propiedades de diseño (preguntas que debes hacerte)

| Propiedad | Pregunta de diseño |
| --- | --- |
| Reproducibilidad | ¿Mismos inputs ⇒ mismos outputs? |
| Idempotencia | ¿Re-ejecutar es seguro? (¿sobrescribes o duplicas?) |
| Observabilidad | ¿Sé cuántas filas caí y por qué? |
| Fail-fast | ¿Prefiero abortar a publicar basura? |
| Contrato de esquema | ¿Qué columnas son obligatorias? |

---

## B2. Anatomía del demo `pipeline_ventas.py`

| Función | Rol |
| --- | --- |
| `REQUIRED_COLUMNS` | Contrato de entrada |
| `setup_logging` | Consola (+ fichero en E4) |
| `load` | I/O + existencia + columnas |
| `transform` | Limpieza + `importe` + report |
| `save` | CSV limpio + `metrics.json` |
| `main` | CLI (`argparse`) + gate + exit codes |

### Columnas del contrato

`fecha, region, producto, unidades, precio_unitario, cliente_id`

**Checkpoint del CSV del curso:** ~**140 válidas / 10 inválidas** → `error_rate ≈ 0.067`.

---

## B3. Guion de exposición (30 min)

1. Mensaje: notebook ≠ job (5 min).  
2. Dibujar etapas A1 + lanzar demo OK (8 min).  
3. Señalar `transform` puro vs `load`/`save` (7 min).  
4. Forzar umbral `0.05` y leer exit code + metrics (10 min).

---

## B4. Exit codes: convención del curso

| Código | Cuándo |
| --- | --- |
| `0` | Éxito |
| `1` | Gate de calidad (`error_rate` alto) |
| `2` | Error de input (fichero/columnas) — E4 |

En bash: `echo $?` justo después del comando.

---

## B5. Logging útil (sin ruido)

- `INFO`: inicio, fin, resumen de filas.  
- `ERROR`: abort, columnas faltantes, path inexistente.  
- No loguear filas enteras con PII en producción.  
- E4: misma traza en consola **y** `run.log`.

---

## B6. Puente al Proyecto II

El Proyecto II pide pipeline + sklearn + IA + tests. Reutiliza este esqueleto:

```text
load → validate/transform → (train/infer) → save metrics → (más adelante) API IA
```

Mantén:

- transform/train **testeables**,
- umbrales y logs,
- `requirements.txt` + CI como en el Proyecto I.

---

## B7. Anti-patrones frecuentes

1. Todo el pipeline en una sola celda de notebook.  
2. `transform` que escribe ficheros por dentro.  
3. Publicar CSV “limpio” sin mirar `error_rate`.  
4. Silenciar excepciones (`except: pass`).  
5. Rutas absolutas (`/Users/yo/...`).  
6. Sin `metrics.json` (“ya lo vi en pantalla”).  
7. Re-ejecutar y **duplicar** salidas sin criterio (rompe idempotencia).  
8. Mezclar descarga HTTP + prompt LLM + pandas en la misma función.  
9. Exit code siempre 0 aunque haya fallado.  
10. Tests que solo lanzan el CLI completo (lentos) y ninguno de `transform`.

---

## B8. Autoevaluación

### Clave

1. ¿Cuáles son las etapas de un data flow en DSIA?  
2. ¿Por qué `transform` no debería hacer I/O?  
3. ¿Qué hace `--max-error-rate 0.05` con el CSV del curso?  
4. ¿Qué hay en `metrics.json`?

### Suplementario

5. ¿Reproducibilidad vs idempotencia?  
6. ¿Exit 1 vs exit 2?  
7. ¿Dónde encaja este pipeline en el Proyecto II?

---

## B9. Checklist de salida

### Conceptos clave

- [ ] Sé explicar el diagrama de etapas  
- [ ] Sé separar load/transform/save en el demo  
- [ ] Sé abortar por umbral y leer el exit code  

### Ejercicio / proyecto

- [ ] E4: contrato de columnas + log a fichero + test de `transform`  
- [ ] Artefactos generados en un `output-dir`  
- [ ] Idea clara de cómo reutilizar esto en Proyecto II  

---

## B10. Para la siguiente sesión (19 oct — APIs IA)

1. Deja el pipeline estable y testeado.  
2. Ojea `02_apis_ia.md`: el cliente IA será **otro borde** (Strategy + mock).  
3. No pegues la llamada OpenAI dentro de `transform`.

---

## B11. Apéndice A — Chuleta

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out \
  --max-error-rate 0.05
echo $?
```

```python
clean, report = transform(df)          # puro
# report: rows_in, rows_out, rows_dropped, error_rate, importe_total
```

---

## B12. Apéndice B — Glosario corto EN/ES

| EN | ES / nota |
| --- | --- |
| data flow / pipeline | flujo de datos / tubería |
| ingestion | ingesta |
| schema / contract | esquema / contrato |
| idempotent | idempotente |
| observability | observabilidad |
| fail-fast | fallar pronto |
| exit code | código de salida |
| side effect | efecto lateral (I/O) |

---

## B13. Apéndice C — Preguntas típicas de clase

**¿Puedo seguir usando notebooks?**  
Sí para explorar. El **entregable** del flujo es un script/CLI con artefactos.

**¿Obligatorio abortar si hay errores?**  
Debes poder **decidir** con un umbral. Publicar siempre sin gate no es aceptable en DSIA.

**¿Cuántas métricas mínimo?**  
Las del report del demo + las que pida tu dominio en Proyecto II.

**¿El test tiene que lanzar `main()`?**  
Primero testea `transform`. El CLI puede tener un smoke test aparte.

**¿Datos grandes?**  
Misma arquitectura; en clase usamos `ventas.csv` pequeño a propósito.

---

## B14. Apéndice D — Mini rúbrica de autocontrol

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Etapas | Todo mezclado | load/transform/save visibles | + contrato de columnas |
| Testabilidad | Solo CLI manual | Test de `transform` | + tmp_path en load/save |
| Calidad | Siempre escribe | Umbral + exit code | Log fichero + metrics ricos |
| Proyecto II | Empieza de cero | Reutiliza el esqueleto | Listo para IA/sklearn en bordes |

---

## 14. Cierre

Si dominas la **Parte A**, tienes lo esencial de la sesión:

> **Pipeline por etapas + lógica pura testeable + gate de calidad con métricas y exit codes.**

**Siguiente paso inmediato:** haz [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) y conecta el mismo patrón a tu repo del Proyecto II.
