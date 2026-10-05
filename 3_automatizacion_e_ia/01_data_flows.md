# Sesión 5 oct 2026 — Flujos de datos (automatizar el pipeline)

| Recurso | Fichero |
| --- | --- |
| Demo | [`ejemplos/pipeline_ventas.py`](ejemplos/pipeline_ventas.py) |
| Ejercicio de clase | [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) |
| Datos | [`Datos/ventas.csv`](Datos/ventas.csv) |
| Base previa (arquitectura) | [`../1_programacion_avanzada_python/03_arquitectura_patrones.md`](../1_programacion_avanzada_python/03_arquitectura_patrones.md) |

Este documento es la **referencia amplia** de automatización de data flows en DSIA: qué hace que un pipeline sea un **job** (no un notebook), los **tres conceptos clave** de automatización que debes dominar al salir de clase, y material suplementario (etapas del flow, I/O vs puro, cron, CI, anti-patrones, puente al Proyecto II).

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar la sesión **debes** ser capaz de:

1. Lanzar el flujo como **job parametrizado por CLI** (sin notebook, sin inputs interactivos).
2. Exponer **señales para máquinas**: exit codes + `metrics.json` + logs (para shell, cron y CI).
3. Dejar el job **seguro de re-ejecutar**: idempotencia + gate de calidad (fail-fast).

### Deseables (material suplementario)

4. Describir el flow por etapas (ingesta → transform → persistencia → observabilidad).
5. Separar I/O de `transform` y testear el núcleo en memoria.
6. Programar el job con **cron** y/o **encadenar scripts** (`&&`, orquestador, contratos de paths).
7. Extender el demo (E4) y enlazarlo al **Proyecto II**.

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos

En DSIA no entregamos “un notebook que limpia ventas si pulso Run All”. Entregamos un **job automatizable** que otra persona (o cron/CI) pueda lanzar:

```bash
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir Datos/salida
```

y obtener artefactos + evidencia de calidad **sin que nadie esté delante**.

### 1.2 Mapa mental del semestre

```text
Tema 1  →  pandas + arquitectura (etapas y módulos)
Tema 2  →  pytest + CI (confianza en el código)
Tema 3  →  automatizar el flujo de datos (hoy) + APIs IA
Tema 5  →  E2E / deploy                    ← el mismo job crece
```

Automatizar = el trabajo ocurre **sin ti**: mismos comandos, señales claras, re-ejecución segura.

### 1.3 Analogías útiles

| Concepto | Analogía |
| --- | --- |
| Job automatizable | Turno de fábrica que arranca solo (cron/CI) |
| CLI parametrizada | Misma máquina, distinta materia prima / umbral |
| Exit code | Semáforo para el siguiente robot de la línea |
| `metrics.json` / `run.log` | Parte de producción + libro de incidencias |
| Idempotencia | Pulsar “guardar” dos veces no crea dos facturas |
| Gate / fail-fast | Si hay >X % defectuoso, paramos y no publicamos |
| Data flow (etapas) | Cadena de montaje (arquitectura; ver Parte B) |
| `transform` puro | Máquina interna testeable sin salir de la nave |

### 1.4 Regla de oro

> **Si una máquina no puede lanzarlo, leer el resultado y re-ejecutarlo sin miedo, aún no está automatizado.**

---

# PARTE A — Tres conceptos clave (obligatorio)

> Prioridad de clase: A1 → A2 → A3.  
> Las **etapas** del pipeline y la separación I/O/`transform` importan, pero son la **arquitectura que habilita** la automatización (Parte B). Hoy el foco es: *¿puede correr solo?*

---

## A1. Concepto clave 1 — Job parametrizado (CLI, no notebook)

### Qué es

Un flujo está automatizado solo si existe un **entrypoint** que:

1. se lanza con un comando,
2. recibe **parámetros** (input, output, umbrales),
3. no pide `input()` ni “ejecuta la celda 4”,
4. escribe artefactos en rutas conocidas.

```text
Humano / cron / CI
        │
        ▼
python pipeline_ventas.py --input … --output-dir … --max-error-rate …
        │
        ▼
artefactos + señales (A2)
```

### Demo mínima

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5
```

Misma lógica, otra política (sin tocar código):

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/prod \
  --max-error-rate 0.05
```

### Por qué es *el* concepto #1 de automatización

Sin CLI estable, no hay cron, no hay CI de datos, no hay compañero que reproduzca tu pipeline. El notebook explora; el **job** opera.

### Checklist del concepto 1

- [ ] Sé lanzar el demo solo con flags
- [ ] Sé cambiar input / output / umbral sin editar el `.py`
- [ ] Sé explicar por qué un “Run All” no es automatización

---

## A2. Concepto clave 2 — Señales para máquinas (exit + metrics + logs)

### Qué es

Quien automatiza (shell, cron, Actions) no mira la pantalla: lee **señales**.

| Señal | Para qué sirve |
| --- | --- |
| Exit code `0` / `1` / `2` | ¿Sigo? ¿Alarma de datos? ¿Alarma de config? |
| `metrics.json` | Evidencia numérica de la corrida |
| `run.log` (y/o stdout redirigido) | Diagnóstico cuando nadie estaba delante |

En el demo:

```python
if report["error_rate"] > args.max_error_rate:
    logger.error("... abortando")
    return 1
# ...
return 0
```

| Código | Significado | Quién reacciona |
| --- | --- | --- |
| `0` | OK: artefactos escritos | Encadena el siguiente paso |
| `1` | Gate de calidad | Alerta de datos; no “publiques” |
| `2` | Input inválido (path/columnas) | Alerta de configuración |

### Práctica en aula

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out \
  --max-error-rate 0.05
echo $?   # 1  →  el CSV del curso (~0.067) no pasa el umbral

# Happy path + leer evidencia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ok \
  --max-error-rate 0.5
cat /tmp/ok/metrics.json
tail -n 20 /tmp/ok/run.log
```

Composición (la señal gobierna el siguiente paso):

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/ok --max-error-rate 0.5 \
&& echo "OK: siguiente paso automatizado" \
|| echo "KO: no publiques"
```

### Checklist del concepto 2

- [ ] Sé interpretar `echo $?` tras el pipeline
- [ ] Sé distinguir exit `1` (datos) vs `2` (config/input)
- [ ] Sé apuntar a `metrics.json` y al log como evidencia de una corrida “a solas”

---

## A3. Concepto clave 3 — Seguro de re-ejecutar (idempotencia + gate)

### Qué es

Automatizar implica **volver a lanzar** (cron diario, reintento, CI). Dos propiedades:

1. **Idempotencia** — N ejecuciones al mismo destino → resultado predecible (sobrescribe; no duplica basura).  
2. **Gate / fail-fast** — si la calidad no llega, **no publiques** (no escribas el CSV “limpio” o no encadenes el siguiente paso).

```bash
# Idempotencia: mismo output-dir dos veces
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem
# Esperado: ventas_limpias.csv, metrics.json, run.log  (una vez cada uno)
```

```bash
# Gate: no “aprobar” una corrida mala
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/gate --max-error-rate 0.05
echo $?   # 1 — aborta antes de tratarla como éxito
```

**Checkpoint del CSV del curso:** ~**140 válidas / 10 inválidas** → `error_rate ≈ 0.067`.

### Por qué importa

Un cron que cada noche **añade** otro `ventas_limpias (3).csv` o publica basura con exit `0` no es automatización: es deuda operativa.

### Checklist del concepto 3

- [ ] Sé re-ejecutar sobre el mismo `output-dir` sin duplicar artefactos
- [ ] Sé forzar un rojo con `--max-error-rate 0.05` y explicar el fail-fast
- [ ] Sé decir por qué cron exige idempotencia + señales claras (A2)

---

## A4. Mapa mental de los 3 conceptos

```text
CLI parametrizada     →  una máquina puede lanzarlo
Exit + metrics + logs →  una máquina puede decidir / diagnosticar
Idempotencia + gate   →  una máquina puede re-lanzarlo sin miedo
```

Arquitectura (Parte B): etapas del flow + `transform` puro hacen que ese job sea mantenible y testeable — pero **no sustituyen** a A1–A3.

**Siguiente paso inmediato en clase:** [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md).

---

# PARTE B — Material suplementario

> Úsalo para profundizar y para el Proyecto II. **No** sustituye a A1–A3.  
> Aquí entran la **arquitectura del flow** (etapas, I/O vs puro) y el detalle de cron/CI.

---

## B0. Arquitectura que habilita la automatización

Los conceptos clave hablan de *lanzar / señalar / re-lanzar*. Para que eso sea mantenible hace falta un flow por etapas y un núcleo testeable.

### Etapas

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

### I/O vs lógica pura

| Capa | Puede tocar disco/red | Debe ser fácil de testear |
| --- | --- | --- |
| `load` / `save` | Sí | Con `tmp_path` o mocks |
| `transform(df) -> (clean, report)` | **No** (idealmente) | Con DataFrame en memoria |

```python
def test_transform_report_counts():
    df = pd.DataFrame({
        "unidades": [1, None, 2],
        "precio_unitario": [10.0, 5.0, -1.0],
    })
    clean, report = transform(df)
    assert report["rows_in"] == 3
    assert report["rows_dropped"] >= 1
```

Sin esta separación, puedes “automatizar” un monolito frágil: corre solo, pero no lo puedes testear ni cambiar el origen de datos sin miedo.

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

El exit code es el enchufe hacia el resto del mundo. Automatizar de verdad suele ser **encadenar varios scripts/jobs**, no solo lanzar uno.

### B4.1 Encadenación de scripts

#### Idea

```text
script A (limpiar) ──exit 0──► script B (publicar / validar metrics)
        │                              │
        └──exit ≠ 0──► STOP (no B)     └──exit 0──► script C (avisar / train)
```

Cada eslabón:

1. es un **CLI** con flags,
2. escribe artefactos en rutas conocidas,
3. devuelve exit code útil,
4. el siguiente **solo** corre si el anterior fue `0`.

#### Operadores que debes dominar

| Forma | Comportamiento |
| --- | --- |
| `cmd1 && cmd2` | `cmd2` solo si `cmd1` salió `0` |
| `cmd1 \|\| cmd2` | `cmd2` solo si `cmd1` **falló** |
| `cmd1 ; cmd2` | `cmd2` **siempre** (peligroso en pipelines) |
| `set -euo pipefail` | el script bash aborta al primer comando ≠ 0 |

Regla: en un orquestador de datos preferimos `&&` o `set -e`, casi nunca `;` entre pasos críticos.

#### Ejemplo mínimo (2 pasos)

```bash
IN=Datos/ventas.csv
OUT=/tmp/cadena_demo
PUB=/tmp/cadena_demo/publicado

python ejemplos/pipeline_ventas.py \
  --input "$IN" \
  --output-dir "$OUT" \
  --max-error-rate 0.5 \
&& mkdir -p "$PUB" \
&& cp "$OUT/ventas_limpias.csv" "$PUB/" \
&& cp "$OUT/metrics.json" "$PUB/" \
&& echo "Publicado en $PUB"
```

Si el gate falla (`exit 1`), **no** se copia nada a `publicado/`.

#### Orquestador multi-script (patrón DSIA)

Imagina tres piezas (en el Proyecto II las tendrás de verdad; aquí B y C son stubs didácticos):

| Paso | Script | Entrada | Salida |
| --- | --- | --- | --- |
| 1 | `pipeline_ventas.py` | CSV crudo | `ventas_limpias.csv` + `metrics.json` |
| 2 | `check_metrics.py` | `metrics.json` | exit `0/1` según reglas |
| 3 | `notify_ok.sh` | — | mensaje / fichero de “listo” |

Stub de comprobación (guárdalo p. ej. como `ejemplos/check_metrics.py` en tu práctica):

```python
#!/usr/bin/env python3
"""Falla si error_rate o rows_out no cumplen umbrales."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", type=Path, required=True)
    p.add_argument("--max-error-rate", type=float, default=0.1)
    p.add_argument("--min-rows-out", type=int, default=1)
    args = p.parse_args()

    report = json.loads(args.metrics.read_text(encoding="utf-8"))
    if report["error_rate"] > args.max_error_rate:
        print(f"KO error_rate={report['error_rate']}", file=sys.stderr)
        return 1
    if report["rows_out"] < args.min_rows_out:
        print(f"KO rows_out={report['rows_out']}", file=sys.stderr)
        return 1
    print(f"OK metrics {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Stub de notificación:

```bash
#!/usr/bin/env bash
# ejemplos/notify_ok.sh
set -euo pipefail
stamp="${1:-$(date -Iseconds)}"
echo "PIPELINE_OK ${stamp}" | tee "Datos/salida/LAST_OK.txt"
```

Orquestador que los encadena (`scripts/run_cadena_ventas.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
DAY="$(date +%F)"
OUT="Datos/salida/${DAY}"
mkdir -p "$OUT"

echo "== 1/3 limpiar =="
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir "$OUT" \
  --max-error-rate 0.5

echo "== 2/3 validar metrics =="
python ejemplos/check_metrics.py \
  --metrics "$OUT/metrics.json" \
  --max-error-rate 0.1 \
  --min-rows-out 100

echo "== 3/3 notificar =="
bash ejemplos/notify_ok.sh "$DAY"

echo "Cadena completa OK → $OUT"
```

```bash
chmod +x scripts/run_cadena_ventas.sh ejemplos/notify_ok.sh
./scripts/run_cadena_ventas.sh
echo "exit=$?"
```

Con `set -e`, si el paso 1 o 2 falla, **no** se ejecuta el 3: no hay falso “PIPELINE_OK”.

#### Variante explícita con `&&` (sin `set -e`)

```bash
OUT=/tmp/cadena
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5 \
&& python ejemplos/check_metrics.py --metrics "$OUT/metrics.json" --max-error-rate 0.1 --min-rows-out 100 \
&& bash ejemplos/notify_ok.sh \
|| { echo "Cadena abortada en algún eslabón"; exit 1; }
```

#### Contratos entre scripts (imprescindible)

Al encadenar, acuerda **paths y formatos**, no “lo que salió por pantalla”:

| Contrato | Ejemplo |
| --- | --- |
| Path de entrada del paso N+1 | `$OUT/ventas_limpias.csv` |
| Path de métricas | `$OUT/metrics.json` |
| Campos JSON esperados | `error_rate`, `rows_out`, … |
| Exit codes | mismos significados en todos los CLIs |

Sin contrato, la cadena se rompe en silencio o con rutas inventadas.

#### Anti-patrones al encadenar

1. `paso1 ; paso2` — el 2 corre aunque el 1 haya fallado.  
2. Ignorar `$?` y mirar solo el log a ojo.  
3. Paso 2 que relee el CSV crudo en vez del artefacto del paso 1.  
4. Un único script gigante “que lo hace todo” sin bordes reutilizables.  
5. Notificar éxito **antes** de comprobar metrics.

### B4.2 Wrapper para cron

`cron` no “entiende” tu repo: llama a un **script** con paths absolutos, venv y logs.

Guarda p. ej. `scripts/run_pipeline_ventas.sh` (ajusta `REPO` a tu máquina):

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia"
VENV="/Users/TU_USUARIO/icai/dsia-26-27/.venv"   # o el venv del curso
DAY="$(date +%F)"
OUT="${REPO}/Datos/salida/${DAY}"
LOG_DIR="${REPO}/Datos/salida/cron_logs"
mkdir -p "${OUT}" "${LOG_DIR}"

# PATH mínimo + activar venv (cron arranca con un entorno muy pobre)
export PATH="/usr/local/bin:/usr/bin:/bin"
# shellcheck source=/dev/null
source "${VENV}/bin/activate"

cd "${REPO}"
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir "${OUT}" \
  --max-error-rate 0.1 \
  >> "${LOG_DIR}/ventas_${DAY}.log" 2>&1

echo "OK ${DAY} exit=0" >> "${LOG_DIR}/ventas_${DAY}.log"
```

```bash
chmod +x scripts/run_pipeline_ventas.sh
# Prueba manual antes de cron:
./scripts/run_pipeline_ventas.sh
echo $?
```

`set -e` + exit del pipeline: si el gate falla (`1`) o el input es inválido (`2`), el script aborta y **no** imprime el `OK`.

### B4.3 Crontab: ejemplos concretos

Sintaxis (5 campos + comando):

```text
┌──────── minuto (0–59)
│ ┌────── hora (0–23)
│ │ ┌──── día del mes (1–31)
│ │ │ ┌── mes (1–12)
│ │ │ │ ┌ día de la semana (0–7, 0 y 7 = domingo)
│ │ │ │ │
* * * * *  comando
```

Editar la tabla del usuario:

```bash
crontab -e          # editar
crontab -l          # listar
```

Ejemplos (sustituye la ruta del wrapper):

```cron
# Cada día a las 02:15 — cierre nocturno de ventas
15 2 * * * /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia/scripts/run_pipeline_ventas.sh

# Cada hora en punto (útil en pruebas; no lo dejes así en “prod” de juguete)
0 * * * * /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia/scripts/run_pipeline_ventas.sh

# Lunes a viernes a las 07:30 — corrida laborable
30 7 * * 1-5 /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia/scripts/run_pipeline_ventas.sh

# Domingo a las 03:00 — corrida semanal
0 3 * * 0 /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia/scripts/run_pipeline_ventas.sh
```

Variante **sin** script aparte (menos mantenible; solo para entender cron):

```cron
15 2 * * * cd /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia && /Users/TU_USUARIO/icai/dsia-26-27/.venv/bin/python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir Datos/salida/$(date +\%F) --max-error-rate 0.1 >> Datos/salida/cron_logs/ventas.log 2>&1
```

Nota: en crontab, `%` hay que escaparlo como `\%` (cron lo interpreta de forma especial).

### B4.4 Comprobar que cron “disparó”

```bash
# macOS: logs del sistema (según versión)
log show --predicate 'process == "cron"' --last 2h | tail

# Linux típico
grep CRON /var/log/syslog | tail
# o:
journalctl -u cron -n 50
```

Y en el repo:

```bash
ls Datos/salida/cron_logs/
tail -n 40 Datos/salida/cron_logs/ventas_$(date +%F).log
cat Datos/salida/$(date +%F)/metrics.json
```

### B4.5 Pitfalls típicos de cron (lista corta)

1. **PATH vacío** — usa venv con path absoluto o `source` del `activate`.  
2. **Rutas relativas** — `cd` al repo o paths absolutos siempre.  
3. **Sin `chmod +x`** en el `.sh`.  
4. **Sin redirigir logs** — “no pasó nada” porque stdout de cron se pierde.  
5. **Probar solo en crontab** — primero ejecuta el wrapper a mano y mira `echo $?`.  
6. **Máquina dormida** — en un portátil, si está suspendido a las 02:15, esa corrida no corre (en clase basta entenderlo).

### B4.6 CI como consumidor del job

En Tema 2 ya automatizaste **validar código**. Aquí automatizas **procesar datos**. Encajan:

```text
push/PR  →  pytest (transform puro, cov)     ← calidad del código
cron     →  pipeline CLI + leer metrics/log  ← calidad del dato / corrida
CI       →  puede smoke-testear el mismo CLI
```

No hace falta Airflow en DSIA: CLI + exit codes + tests + cron bastan para el Proyecto II.

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

1. Mensaje: automatizar = CLI + señales + re-ejecución segura (5 min).  
2. A1: lanzar demo con flags; cambiar umbral sin tocar código (7 min).  
3. A2: forzar exit `1` con `0.05`; leer `metrics.json` / log; mostrar `&&` (10 min).  
4. A3: re-run idempotente + adelanto cron (B4) (8 min).  
5. (Si sobra) B0: etapas + `transform` puro como arquitectura de soporte.

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

Escenario: cada noche quieres limpiar ventas y dejar métricas en una carpeta con fecha. El cuerpo del script es el mismo que pondrías detrás de `15 2 * * *` en crontab (véase B4.3).

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

1. ¿Qué hace que un pipeline sea un *job* automatizable (y no un notebook)?  
2. ¿Qué señales lee una máquina tras la corrida? ¿Exit `1` vs `2`?  
3. ¿Por qué cron exige idempotencia?  
4. ¿Qué hace `--max-error-rate 0.05` con el CSV del curso?

### Suplementario

5. ¿Cuáles son las etapas del data flow?  
6. ¿Por qué `transform` no debería hacer I/O?  
7. ¿Cómo encadenas **varios scripts** para que el 3.º no corra si falló el 1.º?  
8. ¿Qué contrato (paths/JSON/exit) pasas entre eslabones?  
9. ¿Qué pone una línea de crontab y por qué el wrapper usa paths absolutos?

---

## B13. Checklist de salida

### Conceptos clave (automatización)

- [ ] Sé lanzar el job solo con CLI / flags  
- [ ] Sé interpretar exit codes y leer `metrics.json` + log  
- [ ] Sé re-ejecutar de forma idempotente y abortar por umbral  

### Arquitectura / profundidad

- [ ] Sé dibujar las etapas del flow  
- [ ] Sé separar load/transform/save y testear `transform`  
- [ ] Sé encadenar scripts con `&&` / `set -e` y contratos de paths  
- [ ] Sé explicar una línea de crontab + wrapper con paths absolutos  

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

# Composición / encadenación
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/ok --max-error-rate 0.5 \
&& echo "siguiente paso automatizado"

# Cadena multi-script (tras crear stubs + orquestador; ver B4.1)
./scripts/run_cadena_ventas.sh
echo $?

# Cron (tras crear el wrapper)
./scripts/run_pipeline_ventas.sh
crontab -l
# Ejemplo de línea:
# 15 2 * * * /ruta/absoluta/.../scripts/run_pipeline_ventas.sh
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

**¿Obligatorio usar cron en el Proyecto II?**  
No como requisito rígido. Sí debes dejar el job **cron-ready** (CLI + exit codes + logs). Programarlo en tu máquina es la prueba de fuego de la automatización.

---

## B18. Apéndice D — Mini rúbrica de autocontrol

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Job CLI | Notebook / paths fijos | Flags input/output/umbral | Listo para cron (wrapper + logs) |
| Señales | Solo print en pantalla | Exit codes + metrics | + log fichero + composición `&&` |
| Re-ejecución | Duplica artefactos / siempre exit 0 | Idempotente + gate | Cron diario verificable |
| Arquitectura | Todo mezclado | load/transform/save visibles | + test de `transform` |
| Proyecto II | Empieza de cero | Reutiliza el esqueleto | Listo para IA/sklearn en bordes |

---

## 14. Cierre

Si dominas la **Parte A**, tienes lo esencial de la sesión:

> **CLI parametrizada + señales (exit/metrics/logs) + re-ejecución segura (idempotencia + gate) = flujo automatizable.**

La Parte B (etapas, `transform` puro, cron) es lo que hace ese job **mantenible y operable** en el tiempo.

**Siguiente paso inmediato:** haz [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) y conecta el mismo patrón a tu repo del Proyecto II.
