# Sesión 5 oct 2026 — Flujos de datos (data flows)

| Recurso | Fichero |
| --- | --- |
| Demo | [`ejemplos/pipeline_ventas.py`](ejemplos/pipeline_ventas.py) |
| Ejercicio de clase | [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) |
| Datos | [`Datos/ventas.csv`](Datos/ventas.csv) |
| Base previa (arquitectura) | [`../1_programacion_avanzada_python/03_arquitectura_patrones.md`](../1_programacion_avanzada_python/03_arquitectura_patrones.md) |

Este documento es la **referencia amplia** de data flows en DSIA: por qué un pipeline no es un notebook, los **tres conceptos clave** que debes dominar al salir de clase, y material suplementario (propiedades de automatización, parametrización CLI, composición con shell/CI, exit codes, anti-patrones, puente al Proyecto II) para automatizar con criterio.

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar la sesión **debes** ser capaz de:

1. Describir un **data flow** por etapas: ingesta → validación/transformación → persistencia → observabilidad.
2. Separar **I/O** (load/save) de la **lógica pura** (`transform`) testeable sin disco.
3. Aplicar un **gate de calidad** (`max-error-rate` + logs + `metrics.json` + exit codes).

### Deseables (material suplementario)

4. Nombrar y ejemplificar: reproducibilidad, idempotencia, observabilidad, fail-fast, parametrización.
5. Encadenar el job con shell (`&&`, `echo $?`) y entenderlo como pieza de CI/cron.
6. Extender el demo (E4): contrato, log a fichero, re-ejecución idempotente, test de `transform`.
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
| Job automatizable | Turno de fábrica que arranca solo (cron/CI), no “cuando me acuerdo” |
| Ingesta (`load`) | Recepción de materia prima |
| `transform` puro | Máquina que procesa sin salir de la nave |
| Persistencia (`save`) | Almacén de producto terminado |
| `metrics.json` | Parte de producción del turno |
| `run.log` | Cámara / libro de incidencias |
| `max-error-rate` | “Si hay >X % defectuoso, paramos la línea” |
| Exit code ≠ 0 | Alarma roja para CI o el operador |
| Idempotencia | Pulsar “guardar” dos veces no crea dos facturas |
| Parametrización CLI | Misma máquina, distinta materia prima / umbral |
| Composición (`&&`) | Solo pasa a la siguiente estación si la anterior OK |

### 1.4 Regla de oro

> **I/O en los bordes; reglas de negocio en el centro; si la calidad no llega, no publiques; el job debe poder lanzarlo una máquina sin ti delante.**

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

## B1. Propiedades de automatización (con ejemplos)

| Propiedad | Pregunta de diseño | Ejemplo en el demo / E4 |
| --- | --- | --- |
| Reproducibilidad | ¿Mismos inputs ⇒ mismos outputs? | Mismo CSV + mismos flags → mismo `metrics.json` |
| Idempotencia | ¿Re-ejecutar es seguro? | Dos runs al mismo `--output-dir` sobrescriben, no duplican |
| Observabilidad | ¿Sé cuántas filas caí y por qué? | `run.log` + `metrics.json` + exit code |
| Fail-fast | ¿Aborto antes de publicar basura? | `--max-error-rate 0.05` → exit `1` sin `save` |
| Contrato de esquema | ¿Qué columnas son obligatorias? | `REQUIRED_COLUMNS` → exit `2` si faltan |
| Parametrización | ¿Cambio input/umbral sin editar código? | `--input`, `--output-dir`, `--max-error-rate` |
| Componibilidad | ¿Otro script/CI puede encadenarlo? | Exit codes + CLI estable |

### B1.1 Reproducibilidad — ejemplo

```bash
# Dos máquinas / dos días: mismos argumentos → mismos conteos
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/run_a \
  --max-error-rate 0.5

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/run_b \
  --max-error-rate 0.5

diff /tmp/run_a/metrics.json /tmp/run_b/metrics.json   # sin diferencias esperables
```

Si el resultado depende de “qué celda ejecuté antes” en un notebook, **no** es reproducible como job.

### B1.2 Idempotencia — ejemplo

```bash
OUT=/tmp/idem_demo
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5
ls "$OUT"
# Esperado: ventas_limpias.csv, metrics.json, run.log  (una vez cada uno)
```

Mal patrón: append infinito a un CSV o nombres con timestamp sin control (`ventas_limpias_171234.csv` × N) cuando el consumidor espera un path fijo.

### B1.3 Observabilidad — ejemplo de lectura

Tras una corrida OK, un operador (o tú a las 3:00) debe poder responder sin depurar a mano:

```bash
cat Datos/salida/metrics.json
# rows_in, rows_out, rows_dropped, error_rate, importe_total

tail -n 30 Datos/salida/run.log
```

### B1.4 Fail-fast + contrato — ejemplos

```bash
# Gate de calidad (datos “sucios” por encima del umbral)
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/gate --max-error-rate 0.05
echo $?   # 1

# Input inválido (path que no existe) → código de configuración/input
python ejemplos/pipeline_ventas.py \
  --input Datos/no_existe.csv --output-dir /tmp/x --max-error-rate 0.5
echo $?   # 2
```

**Checkpoint del CSV del curso:** ~**140 válidas / 10 inválidas** → `error_rate ≈ 0.067`.

---

## B2. De notebook a job automatizable

| Notebook (explorar) | Job (automatizar) |
| --- | --- |
| Celdas en orden humano | Un entrypoint (`main`) |
| Paths hardcodeados en la celda | Flags CLI |
| “Ya lo vi en pantalla” | `metrics.json` + logs |
| Re-ejecutar = caos de estado | Idempotente / reproducible |
| Difícil de poner en CI | `pytest` del núcleo + smoke del CLI |

Esqueleto mental:

```text
Explorar en notebook  →  extraer transform()  →  envolver con load/save/CLI  →  gates + logs
```

---

## B3. Parametrización CLI (automatización sin tocar código)

El demo ya parametriza lo esencial:

| Flag | Para qué automatiza |
| --- | --- |
| `--input` | Cambiar fichero (día, entorno, muestra) |
| `--output-dir` | Aislar corridas / staging vs prod local |
| `--max-error-rate` | Política de calidad por entorno |

Ejemplo: misma lógica, dos políticas:

```bash
# Desarrollo: holgado
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/dev --max-error-rate 0.5

# “Prod local”: estricto
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/prod --max-error-rate 0.05
```

Sin flags, cada cambio de umbral sería un commit o un `input()` manual: eso **no** escala a cron/CI.

---

## B4. Componer automatizaciones (shell, cron, CI)

El exit code es el enchufe hacia el resto del mundo.

### B4.1 Encadenar con `&&`

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5 \
&& echo "OK: publicar / siguiente paso" \
|| echo "KO: no publiques ni avises en verde"
```

Solo si el pipeline sale `0` tiene sentido un paso siguiente (copiar a carpeta “publicada”, entrenar un modelo, notificar).

### B4.2 Wrapper mínimo (idea de cron)

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /ruta/al/repo/3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir "Datos/salida/$(date +%F)" \
  --max-error-rate 0.1
```

`set -e` hace que un exit ≠ 0 aborte el script: fail-fast a nivel shell.

### B4.3 CI como consumidor del job

En Tema 2 ya automatizaste **validar código**. Aquí automatizas **procesar datos**. Encajan:

```text
push/PR  →  pytest (transform puro, cov)     ← calidad del código
cron/CI  →  pipeline CLI + leer metrics.json ← calidad del dato / corrida
```

No hace falta Airflow en DSIA: CLI + exit codes + tests bastan para el Proyecto II.

---

## B5. Anatomía del demo `pipeline_ventas.py`

| Función | Rol | Concepto de automatización |
| --- | --- | --- |
| `REQUIRED_COLUMNS` | Contrato de entrada | Fail-fast de esquema |
| `setup_logging` | Consola (+ fichero) | Observabilidad |
| `load` | I/O + existencia + columnas | Borde / contrato |
| `transform` | Limpieza + `importe` + report | Núcleo puro / testeable |
| `save` | CSV limpio + `metrics.json` | Persistencia + evidencia |
| `main` | CLI + gate + exit codes | Job componible |

### Columnas del contrato

`fecha, region, producto, unidades, precio_unitario, cliente_id`

---

## B6. Guion de exposición (30 min)

1. Mensaje: notebook ≠ job automatizable (5 min).  
2. Dibujar etapas A1 + lanzar demo OK + mirar artefactos (8 min).  
3. Señalar `transform` puro vs `load`/`save` (5 min).  
4. Forzar umbral `0.05`, leer exit code + metrics; mostrar re-run idempotente (12 min).

---

## B7. Exit codes: convención del curso

| Código | Cuándo | Quién reacciona |
| --- | --- | --- |
| `0` | Éxito: artefactos escritos | Siguiente paso del script / cron |
| `1` | Gate de calidad (`error_rate` alto) | Alerta: datos malos, no config |
| `2` | Error de input (fichero/columnas) | Alerta: config / contrato |

```bash
python ejemplos/pipeline_ventas.py ... ; echo "exit=$?"
```

---

## B8. Logging útil (sin ruido)

- `INFO`: inicio, fin, resumen de filas.  
- `ERROR`: abort, columnas faltantes, path inexistente.  
- No loguear filas enteras con PII en producción.  
- E4: misma traza en consola **y** `run.log`.

Ejemplo de líneas útiles:

```text
2026-10-05 ... | INFO  | Cargando Datos/ventas.csv
2026-10-05 ... | INFO  | Transformación: {'rows_in': 150, 'rows_dropped': 10, ...}
2026-10-05 ... | ERROR | error_rate 0.067 > max-error-rate 0.050 — abortando
```

---

## B9. Ejemplo guiado: automatizar un “cierre diario”

Escenario: cada noche quieres limpiar ventas y dejar métricas en una carpeta con fecha.

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"   # ajusta a tu layout
DAY="$(date +%F)"
OUT="$ROOT/Datos/salida/$DAY"

python "$ROOT/ejemplos/pipeline_ventas.py" \
  --input "$ROOT/Datos/ventas.csv" \
  --output-dir "$OUT" \
  --max-error-rate 0.1

# Solo llegamos aquí si exit 0
python -c "
import json
from pathlib import Path
m = json.loads(Path('${OUT}/metrics.json').read_text())
assert m['rows_out'] > 0
print(f\"Cierre {m['rows_out']} filas OK; error_rate={m['error_rate']:.3f}\")
"
```

Conceptos que aparecen juntos: parametrización, fail-fast (`set -e` + umbral), observabilidad (`metrics.json`), componibilidad.

---

## B10. Puente al Proyecto II

El Proyecto II pide pipeline + sklearn + IA + tests. Reutiliza este esqueleto:

```text
load → validate/transform → (train/infer) → save metrics → (más adelante) API IA
         ↑ puro                          ↑ bordes I/O / red
```

Mantén:

- `transform` / train **testeables**,
- umbrales, logs y exit codes,
- CLI parametrizable (inputs de train vs infer),
- `requirements.txt` + CI como en el Proyecto I,
- IA **fuera** de `transform` (sesión 19 oct).

---

## B11. Anti-patrones frecuentes

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
11. Umbral o path “mágicos” dentro del código en vez de flags CLI.  
12. Encadenar el siguiente paso **aunque** el pipeline haya salido ≠ 0.

---

## B12. Autoevaluación

### Clave

1. ¿Cuáles son las etapas de un data flow en DSIA?  
2. ¿Por qué `transform` no debería hacer I/O?  
3. ¿Qué hace `--max-error-rate 0.05` con el CSV del curso?  
4. ¿Qué hay en `metrics.json`?

### Suplementario

5. ¿Reproducibilidad vs idempotencia (con un ejemplo cada una)?  
6. ¿Exit 1 vs exit 2?  
7. ¿Cómo encadenas el pipeline en bash para que no “publique” si falla?  
8. ¿Dónde encaja este pipeline en el Proyecto II?

---

## B13. Checklist de salida

### Conceptos clave

- [ ] Sé explicar el diagrama de etapas  
- [ ] Sé separar load/transform/save en el demo  
- [ ] Sé abortar por umbral y leer el exit code  

### Automatización

- [ ] Sé parametrizar input / output / umbral por CLI  
- [ ] Sé re-ejecutar de forma idempotente  
- [ ] Sé encadenar con `&&` / interpretar `echo $?`  
- [ ] Sé leer `run.log` + `metrics.json` como evidencia  

### Ejercicio / proyecto

- [ ] E4 completado (contrato, gate, logs, idempotencia, test)  
- [ ] Artefactos generados en un `output-dir`  
- [ ] Idea clara de cómo reutilizar esto en Proyecto II  

---

## B14. Para la siguiente sesión (19 oct — APIs IA)

1. Deja el pipeline estable, testeado y lanzable por CLI.  
2. Ojea [`02_apis_ia.md`](02_apis_ia.md): el cliente IA será **otro borde** (Strategy + mock).  
3. No pegues la llamada OpenAI dentro de `transform`.

---

## B15. Apéndice A — Chuleta

```bash
cd 3_automatizacion_e_ia

# Happy path
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5

# Gate rojo (CSV del curso)
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out \
  --max-error-rate 0.05
echo $?

# Idempotencia
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem

# Composición
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/ok --max-error-rate 0.5 \
&& echo "siguiente paso automatizado"
```

```python
clean, report = transform(df)          # puro
# report: rows_in, rows_out, rows_dropped, error_rate, importe_total
```

---

## B16. Apéndice B — Glosario corto EN/ES

| EN | ES / nota |
| --- | --- |
| data flow / pipeline | flujo de datos / tubería |
| job / batch job | trabajo por lotes automatizable |
| ingestion | ingesta |
| schema / contract | esquema / contrato |
| idempotent | idempotente |
| observability | observabilidad |
| fail-fast | fallar pronto |
| exit code | código de salida |
| side effect | efecto lateral (I/O) |
| parameterization | parametrización (CLI/env) |
| scheduling (cron) | programación temporal |
| composability | componibilidad (encadenar jobs) |

---

## B17. Apéndice C — Preguntas típicas de clase

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

**¿Necesito Airflow / Prefect / Dagster?**  
No en DSIA. Domina CLI + exit codes + tests; los orquestadores son el mismo diseño a escala.

**¿Idempotencia implica borrar siempre la carpeta?**  
No: sobrescribir paths estables (`ventas_limpias.csv`, `metrics.json`) suele bastar. Lo importante es un resultado predecible tras N ejecuciones.

---

## B18. Apéndice D — Mini rúbrica de autocontrol

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Etapas | Todo mezclado | load/transform/save visibles | + contrato de columnas |
| Testabilidad | Solo CLI manual | Test de `transform` | + tmp_path en load/save |
| Calidad | Siempre escribe | Umbral + exit code | Log fichero + metrics ricos |
| Automatización | Paths fijos / notebook | CLI parametrizada | + idempotencia + composición `&&`/CI |
| Proyecto II | Empieza de cero | Reutiliza el esqueleto | Listo para IA/sklearn en bordes |

---

## 14. Cierre

Si dominas la **Parte A**, tienes lo esencial de la sesión:

> **Pipeline por etapas + lógica pura testeable + gate de calidad con métricas y exit codes.**

Si además manejas la **automatización** de la Parte B (parametrización, idempotencia, composición):

> **El mismo job lo puede lanzar una persona, un cron o CI — y sabrás si publicar o no.**

**Siguiente paso inmediato:** haz [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) y conecta el mismo patrón a tu repo del Proyecto II.
