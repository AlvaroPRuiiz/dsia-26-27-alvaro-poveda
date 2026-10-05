# Sesión 5 oct 2026 — Automatizar un flujo de datos

| Recurso | Fichero |
| --- | --- |
| Demo | [`ejemplos/pipeline_ventas.py`](ejemplos/pipeline_ventas.py) |
| Ejercicio de clase | [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md) |
| Datos | [`Datos/ventas.csv`](Datos/ventas.csv) (~140 válidas / 10 inválidas) |
| Base previa | [`../1_programacion_avanzada_python/03_arquitectura_patrones.md`](../1_programacion_avanzada_python/03_arquitectura_patrones.md) |

## Historia de la sesión (léela primero)

Hoy no aprendes “otro script de pandas”. Aprendes a convertir un flujo de datos en un **job que puede correr solo**:

```text
1. Lo lanzas con un comando (CLI)     →  Parte A1
2. Una máquina entiende el resultado  →  Parte A2  (exit + metrics + logs)
3. Puedes volver a lanzarlo sin miedo →  Parte A3  (idempotencia + gate)
4. Lo pegas con bash / lo encadenas   →  Parte B   (shell, cadena, cron)
5. El código por dentro es mantenible →  Parte B   (etapas + transform puro)
```

**Regla de oro:** si una máquina no puede lanzarlo, leer el resultado y re-ejecutarlo sin miedo, **aún no está automatizado**.

En clase: exposición (~30 min, Parte A) → ejercicio [`E4`](ejercicios/E4_pipeline.md) (~50 min, A + B).

---

## 0. Objetivos

### Obligatorios (Parte A)

1. Lanzar el flujo como **job CLI** parametrizado (`--input`, `--output-dir`, `--max-error-rate`).
2. Exponer **señales**: exit `0/1/2` + `metrics.json` + `run.log`.
3. Dejarlo **seguro de re-ejecutar**: idempotencia + gate de calidad.

### Deseables (Parte B)

4. Usar **bash** mínimo (`$?`, `&&`, variables, `set -e`, redirecciones).
5. **Encadenar** scripts y dejar un wrapper **cron-ready**.
6. Nombrar etapas del flow y testear `transform` sin disco.
7. Conectar el patrón al **Proyecto II**.

---

## 1. Por qué importa en DSIA

```text
Tema 1  →  pandas + arquitectura
Tema 2  →  pytest + CI          (confianza en el código)
Tema 3  →  automatizar el flujo (hoy) + APIs IA
Tema 5  →  E2E / deploy         (el mismo job crece)
```

Entregamos esto, no un notebook:

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir Datos/salida \
  --max-error-rate 0.5
```

| Idea | Analogía |
| --- | --- |
| Job | Turno de fábrica que arranca solo |
| Flags CLI | Misma máquina, distinta materia prima |
| Exit code | Semáforo para el siguiente robot |
| `metrics.json` / log | Parte de producción + libro de incidencias |
| Idempotencia | Guardar dos veces ≠ dos facturas |
| Bash `&&` | Solo avanza si el semáforo fue verde |

---

# PARTE A — Tres conceptos clave

> Pregunta guía: ***¿puede correr solo?***  
> Orden: **lanzar → señalizar → re-lanzar**. Bash es el pegamento; la arquitectura interna viene en la Parte B.

---

## A1 — Job parametrizado (CLI, no notebook)

Automatizado = existe un **entrypoint** con flags, sin `input()` ni “Run All”.

```text
humano / cron / CI  →  python pipeline_ventas.py --input … --output-dir … --max-error-rate …
                    →  artefactos + señales (A2)
```

```bash
cd 3_automatizacion_e_ia

# Desarrollo (holgado)
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/dev --max-error-rate 0.5

# Otra política, mismo código
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/prod --max-error-rate 0.05
```

| Flag | Qué automatiza |
| --- | --- |
| `--input` | Origen de datos |
| `--output-dir` | Dónde dejar artefactos |
| `--max-error-rate` | Política de calidad |

**Checklist:** lanzo solo con flags · cambio umbral sin editar código · sé por qué el notebook no es un job.

---

## A2 — Señales para máquinas (exit + metrics + logs)

Quien automatiza no mira la pantalla: lee señales.

| Señal | Pregunta que responde |
| --- | --- |
| Exit `0` | ¿Sigo / publico? |
| Exit `1` | ¿Datos malos (gate)? |
| Exit `2` | ¿Config/input roto (path, columnas)? |
| `metrics.json` | ¿Cuántas filas, qué `error_rate`? |
| `run.log` | ¿Qué pasó si nadie estaba delante? |

```bash
# Gate rojo — CSV del curso ≈ 0.067 > 0.05
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/gate --max-error-rate 0.05
echo $?   # 1

# Happy path + evidencia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/ok --max-error-rate 0.5
echo $?   # 0
cat /tmp/ok/metrics.json
tail -n 20 /tmp/ok/run.log

# La señal gobierna el siguiente paso
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/ok --max-error-rate 0.5 \
&& echo "OK: siguiente paso" \
|| echo "KO: no publiques"
```

En el demo, el gate es explícito:

```python
if report["error_rate"] > args.max_error_rate:
    logger.error("... abortando")
    return 1
return 0
```

**Checklist:** interpreto `$?` · distingo `1` vs `2` · sé dónde están metrics y log.

---

## A3 — Seguro de re-ejecutar (idempotencia + gate)

Cron y CI **vuelven a lanzar**. Hace falta:

1. **Idempotencia** — mismo destino N veces → resultado predecible (sobrescribe; no duplica).
2. **Gate** — si la calidad no llega, no publiques / no encadenes (exit `1`).

```bash
# Idempotencia
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem
# Esperado: ventas_limpias.csv, metrics.json, run.log  (una vez cada uno)
```

Checkpoint del curso: ~**140 / 10** → `error_rate ≈ 0.067`.

**Checklist:** re-run sin basura · fuerzo rojo con `0.05` · explico por qué cron exige A2+A3.

---

## A4 — Mapa de los 3 conceptos

```text
A1 CLI          →  puede lanzarlo
A2 señales      →  puede decidir / diagnosticar
A3 idem + gate  →  puede re-lanzarlo sin miedo
        │
        └── bash (Parte B) pega A1–A3 en scripts, cadenas y cron
```

**Siguiente paso en clase:** [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md).

---

# PARTE B — Operar y mantener el job

> La Parte A dice *qué* debe cumplir el job.  
> La Parte B enseña *cómo lo operas* (bash → cadena → cron) y *cómo está construido por dentro* (etapas + `transform`).

---

## B1 — Anatomía del demo

| Pieza | Rol | Concepto |
| --- | --- | --- |
| `REQUIRED_COLUMNS` | Contrato de entrada | Exit `2` si falla |
| `setup_logging` | Consola + `run.log` | Observabilidad |
| `load` | Leer CSV + esquema | Borde I/O |
| `transform` | Limpieza + report | Núcleo puro |
| `save` | CSV limpio + `metrics.json` | Persistencia |
| `main` | CLI + gate + exit codes | Job componible |

Columnas: `fecha, region, producto, unidades, precio_unitario, cliente_id`.

---

## B2 — Arquitectura: etapas + I/O vs puro

```text
Ingesta → Validación/transform → Persistencia → Observabilidad
 (load)      (transform puro)       (save)      (log + metrics + exit)
```

| Capa | ¿Disco/red? | Test |
| --- | --- | --- |
| `load` / `save` | Sí | `tmp_path` |
| `transform(df) → (clean, report)` | No | DataFrame en memoria |

```python
def test_transform_report_counts():
    df = pd.DataFrame({
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        # + resto de columnas del contrato si hace falta
    })
    clean, report = transform(df)
    assert report["rows_in"] == 3
    assert report["rows_dropped"] >= 1
```

Sin esta separación puedes “automatizar” un monolito: corre solo, pero no lo testeas ni cambias el origen de datos con calma.

De notebook a job:

```text
Explorar en notebook → extraer transform() → load/save/CLI → gates + logs → bash/cron
```

---

## B3 — Bash mínimo (el pegamento)

**Python hace el trabajo; bash orquesta el trabajo.**

### Cheatsheet

| Concepto | Ejemplo | Uso |
| --- | --- | --- |
| Shebang | `#!/usr/bin/env bash` | Scripts `.sh` |
| Variable | `OUT=/tmp/run` · `"$OUT"` | Rutas sin repetir |
| Sustitución | `DAY=$(date +%F)` | Carpetas por día |
| Dir del script | `REPO="$(cd "$(dirname "$0")/.." && pwd)"` | Independiente del cwd |
| Exit code | `echo $?` | Leer A2 |
| Encadenar OK | `cmd1 && cmd2` | Solo si exit 0 |
| Alternativa KO | `cmd1 \|\| cmd2` | Mensaje / cleanup |
| Evitar | `cmd1 ; cmd2` | El 2 corre aunque falle el 1 |
| Fail-fast | `set -euo pipefail` | Abortar al primer error |
| Dirs | `mkdir -p "$OUT"` | Idempotente |
| Logs cron | `>> file.log 2>&1` | stdout + stderr |
| Ejecutable | `chmod +x script.sh` | `./script.sh` |

`set -euo pipefail`:

| Flag | Efecto |
| --- | --- |
| `-e` | Comando ≠ 0 → el script muere |
| `-u` | Variable indefinida → error |
| `-o pipefail` | Falla si falla cualquier eslabón del pipe |

### Mini-lab

```bash
cd 3_automatizacion_e_ia
OUT=/tmp/bash_lab
mkdir -p "$OUT"

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5
echo "exit=$?"

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5 \
&& ls "$OUT" && echo "siguiente paso OK" \
|| echo "cadena detenida"
```

---

## B4 — Encadenar scripts

```text
limpiar ──exit 0──► validar metrics ──exit 0──► notificar
   └──≠0── STOP              └──≠0── STOP
```

Cada eslabón: CLI + artefactos en paths conocidos + exit útil.

### Publicar solo si el pipeline OK

```bash
OUT=/tmp/cadena_demo
PUB=/tmp/cadena_demo/publicado

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5 \
&& mkdir -p "$PUB" \
&& cp "$OUT/ventas_limpias.csv" "$OUT/metrics.json" "$PUB/" \
&& echo "Publicado en $PUB"
```

### Orquestador de 3 pasos (patrón E4 / Proyecto II)

| Paso | Script | Contrato |
| --- | --- | --- |
| 1 | `pipeline_ventas.py` | escribe `$OUT/metrics.json` |
| 2 | `check_metrics.py` | lee ese JSON; exit `0/1` |
| 3 | `notify_ok.sh` | solo si 1 y 2 fueron `0` |

Stub `check_metrics.py`:

```python
#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", type=Path, required=True)
    p.add_argument("--max-error-rate", type=float, default=0.1)
    p.add_argument("--min-rows-out", type=int, default=1)
    args = p.parse_args()
    report = json.loads(args.metrics.read_text(encoding="utf-8"))
    if report["error_rate"] > args.max_error_rate or report["rows_out"] < args.min_rows_out:
        print(f"KO {report}", file=sys.stderr)
        return 1
    print(f"OK {report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
#!/usr/bin/env bash
# ejemplos/notify_ok.sh
set -euo pipefail
mkdir -p Datos/salida
echo "PIPELINE_OK ${1:-$(date -Iseconds)}" | tee Datos/salida/LAST_OK.txt
```

```bash
#!/usr/bin/env bash
# scripts/run_cadena_ventas.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
OUT="Datos/salida/$(date +%F)"
mkdir -p "$OUT"

python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5
python ejemplos/check_metrics.py --metrics "$OUT/metrics.json" --max-error-rate 0.1 --min-rows-out 100
bash ejemplos/notify_ok.sh "$(date +%F)"
echo "Cadena OK → $OUT"
```

**Contrato entre pasos:** paths (`$OUT/...`), campos JSON, significados de exit. Sin contrato, la cadena se rompe en silencio.

**Anti-patrones:** `paso1 ; paso2` · notificar éxito antes de validar metrics · que el paso 2 relea el CSV crudo en vez del artefacto del paso 1.

---

## B5 — Cron (programar el job)

### Qué es (en una frase)

**Cron** es un servicio del sistema que, a horas fijas, ejecuta un comando **sin que tú estés delante**.  
La lista de “cuándo → qué” se llama **crontab**.

```text
reloj del SO
    │
    ▼
cron lee tu crontab  →  a las 02:15 lanza el comando  →  tu wrapper .sh  →  pipeline Python
                                                              │
                                                              └─ escribe metrics + log
```

Encaja con la Parte A:

| Concepto | Por qué cron lo necesita |
| --- | --- |
| A1 CLI | Cron solo sabe lanzar un comando |
| A2 señales | Si falla, el exit ≠ 0 y el log lo cuentan (nadie mira la pantalla) |
| A3 idem + gate | Cada noche se re-lanza: no debe duplicar basura ni “aprobar” datos malos |

### Qué **no** es cron

| Cron | No confundir con |
| --- | --- |
| Programa **cuándo** corre el job | El job en sí (eso es tu CLI Python) |
| Una línea “hora + comando” | Un orquestador complejo (Airflow, etc.) |
| Corre en **esa** máquina | CI de GitHub (otra máquina, otro disparador: push/PR) |

En DSIA: **CI** comprueba el código; **cron** (o un schedule) ejecuta la **corrida de datos**.

### Anatomía de una línea de crontab

```text
┌──────── minuto (0–59)
│ ┌────── hora (0–23)
│ │ ┌──── día del mes (1–31)
│ │ │ ┌── mes (1–12)
│ │ │ │ ┌ día semana (0–7; 0 y 7 = domingo)
│ │ │ │ │
* * * * *   comando_a_ejecutar
```

| Campo | `*` significa | Ejemplo |
| --- | --- | --- |
| minuto | cada minuto | `15` → en el minuto 15 |
| hora | cada hora | `2` → a las 02:xx |
| día mes | cada día | `*` → todos |
| mes | cada mes | `*` → todos |
| weekday | cada día | `1-5` → lunes a viernes |

Ejemplos leídos en voz alta:

```cron
15 2 * * *     /ruta/run_pipeline_ventas.sh
# “Cada día, a las 02:15, lanza ese script”

30 7 * * 1-5   /ruta/run_pipeline_ventas.sh
# “De lunes a viernes, a las 07:30”

0 */6 * * *    /ruta/run_pipeline_ventas.sh
# “Cada 6 horas, en el minuto 0”
```

Comandos útiles:

```bash
crontab -e    # editar tu tabla (abre un editor)
crontab -l    # listar lo que tienes programado
```

### Por qué hace falta un **wrapper** `.sh`

Cron **no** es tu terminal interactiva:

| En tu terminal | Cuando lo lanza cron |
| --- | --- |
| Ya hiciste `cd` al repo | Arranca sin cwd conocido |
| El venv puede estar activo | Casi seguro **no** está activo |
| Ves stdout en pantalla | Si no rediriges, el output se pierde |
| `python` está en el PATH | El PATH de cron suele ser mínimo |

Por eso cron no llama a `python ejemplos/pipeline_ventas.py ...` a pelo: llama a un script que **fija** repo, venv, logs y luego lanza el job.

### Receta en 4 pasos

**1. Escribe el wrapper** `scripts/run_pipeline_ventas.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Ajusta estas dos rutas a TU máquina
REPO="/Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia"
VENV="/Users/TU_USUARIO/icai/dsia-26-27/.venv"

DAY="$(date +%F)"
OUT="${REPO}/Datos/salida/${DAY}"
LOG_DIR="${REPO}/Datos/salida/cron_logs"
mkdir -p "${OUT}" "${LOG_DIR}"

# Entorno mínimo + venv (cron no trae el tuyo)
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

Qué hace cada bloque:

| Bloque | Para qué |
| --- | --- |
| `set -euo pipefail` | Si el pipeline sale `1` o `2`, el script aborta (no finge OK) |
| `REPO` / `VENV` absolutos | Cron no sabe dónde estás |
| `OUT` con fecha | Artefactos del día; re-ejecutar el mismo día sobrescribe (idempotencia) |
| `source …/activate` | Mismo Python/deps que en clase |
| `>> log 2>&1` | Guardar stdout **y** stderr para depurar a la mañana |

**2. Prueba a mano** (obligatorio antes de `crontab -e`):

```bash
chmod +x scripts/run_pipeline_ventas.sh
./scripts/run_pipeline_ventas.sh
echo "exit=$?"
tail -n 40 Datos/salida/cron_logs/ventas_$(date +%F).log
cat Datos/salida/$(date +%F)/metrics.json
```

Si aquí falla, cron también fallará: arregla el wrapper primero.

**3. Programa la línea** (sustituye la ruta):

```bash
crontab -e
```

```cron
15 2 * * * /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia/scripts/run_pipeline_ventas.sh
```

**4. Comprueba que disparó** (al día siguiente o tras una prueba con hora cercana):

```bash
crontab -l
ls Datos/salida/cron_logs/
tail -n 50 Datos/salida/cron_logs/ventas_$(date +%F).log
cat Datos/salida/$(date +%F)/metrics.json
```

En clase **basta** con el wrapper + la línea anotada. Instalar cron en el portátil es opcional.

### Variante sin wrapper (solo para entender; no recomendada)

```cron
15 2 * * * cd /Users/TU_USUARIO/icai/dsia-26-27/3_automatizacion_e_ia && /Users/TU_USUARIO/icai/dsia-26-27/.venv/bin/python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir Datos/salida/$(date +\%F) --max-error-rate 0.1 >> Datos/salida/cron_logs/ventas.log 2>&1
```

Notas: hay que escapar `%` como `\%` (cron lo trata especial); la línea es frágil y difícil de mantener → prefiere el `.sh`.

### Fallos típicos

| Síntoma | Causa habitual | Qué hacer |
| --- | --- | --- |
| “No corrió” | Portátil suspendido a esa hora | Entenderlo; en servidor/CI es otro mundo |
| `python: command not found` | PATH / venv | `source` del venv o path absoluto al `python` |
| `No such file` | cwd relativo | `cd "$REPO"` + paths absolutos |
| Log vacío / “no pasó nada” | Sin redirección | `>> archivo.log 2>&1` |
| Corre pero “aprueba” basura | Gate/exit mal | Revisar A2–A3 en el pipeline |
| Duplica ficheros cada noche | Mala idempotencia | Mismos nombres de artefacto, sobrescribir |

### Cron-ready vs “tengo cron instalado”

| Cron-ready (lo pedimos en DSIA) | Cron instalado (opcional) |
| --- | --- |
| CLI estable + exit codes | Línea en `crontab -e` |
| Wrapper con paths/logs | La máquina encendida a esa hora |
| Puedes lanzar el wrapper a mano | Evidencia en `cron_logs/` |

Si el wrapper funciona a mano con `echo $?` y deja metrics/log, el job ya es **automatizable**; cron solo pone el despertador.

---

## B6 — Propiedades (chuleta de diseño)

| Propiedad | Pregunta | En el demo / E4 |
| --- | --- | --- |
| Reproducibilidad | ¿Mismos inputs ⇒ mismos outputs? | Mismos flags → mismo `metrics.json` |
| Idempotencia | ¿Re-ejecutar es seguro? | Mismo `output-dir` sobrescribe |
| Observabilidad | ¿Sé qué pasó? | log + metrics + exit |
| Fail-fast | ¿Aborto antes de publicar basura? | `--max-error-rate` |
| Contrato | ¿Columnas obligatorias? | `REQUIRED_COLUMNS` → exit `2` |
| Parametrización | ¿Sin editar código? | flags CLI |
| Componibilidad | ¿Lo encadena otro script? | exit codes + paths estables |

---

## B7 — Puente al Proyecto II

```text
load → transform → (train/infer sklearn) → save metrics → borde IA (mock en CI)
```

Reutiliza: CLI + exit codes + logs + `transform` testeable + bash/cron.  
La IA **no** va dentro de `transform` (sesión 19 oct).

---

## B8 — Anti-patrones

1. Notebook como entregable operativo.  
2. `transform` que escribe ficheros.  
3. Publicar sin mirar `error_rate`.  
4. Exit siempre `0`.  
5. `paso1 ; paso2` en cadenas de datos.  
6. Paths `/Users/yo/...` sin variable `REPO`.  
7. Cron sin `2>&1`.  
8. Umbral hardcodeado en vez de flag.  
9. Tests solo del CLI completo, ninguno de `transform`.  
10. Mezclar HTTP + LLM + pandas en la misma función.

---

## B9 — Autoevaluación

### Clave

1. ¿Qué hace de un pipeline un *job* (y no un notebook)?  
2. ¿Qué señales lee una máquina? ¿Exit `1` vs `2`?  
3. ¿Por qué cron exige idempotencia + gate?  
4. ¿Qué hace `--max-error-rate 0.05` con el CSV del curso?

### Suplementario

5. ¿Etapas del flow? ¿Por qué `transform` sin I/O?  
6. ¿`set -euo pipefail`? ¿`&&` vs `;`?  
7. ¿Contrato entre scripts de una cadena?  
8. ¿Qué pone una línea de crontab y por qué el wrapper?

---

## B10 — Checklist de salida

**Parte A**

- [ ] CLI con flags; cambio umbral sin editar código  
- [ ] Interpreto `0/1/2` y leo metrics + log  
- [ ] Re-run idempotente; gate `0.05` → exit `1`  

**Parte B**

- [ ] Bash: variables, `$?`, `&&`, `2>&1`, `set -e`  
- [ ] Cadena o wrapper cron-ready  
- [ ] Sé etapas + test de `transform`  
- [ ] E4 hecho / idea clara para Proyecto II  

---

## B11 — Apéndices

### Chuleta bash + pipeline

```bash
cd 3_automatizacion_e_ia
OUT=/tmp/ok; mkdir -p "$OUT"

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5
echo "exit=$?"

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/gate --max-error-rate 0.05
echo $?   # 1

# Cron-ready (tras crear el wrapper)
./scripts/run_pipeline_ventas.sh
# 15 2 * * * /ruta/absoluta/.../scripts/run_pipeline_ventas.sh
```

### Glosario

| EN / símbolo | Nota |
| --- | --- |
| job / batch | trabajo por lotes automatizable |
| exit status (`$?`) | código del último comando |
| `&&` / `\|\|` / `;` | encadenar si OK / si KO / siempre |
| `set -euo pipefail` | fail-fast en scripts |
| redirection (`2>&1`) | mezclar stderr en el log |
| idempotent | re-ejecutar sin efectos indeseados |
| cron | programación temporal |
| shebang | `#!/usr/bin/env bash` |

### FAQ

**¿Notebooks?** Para explorar. El entregable operativo es CLI + artefactos.  
**¿Airflow obligatorio?** No. CLI + exit + bash/cron bastan en DSIA.  
**¿Cron obligatorio en Proyecto II?** No rígido; sí **cron-ready**.  
**¿Idempotencia = borrar carpeta?** No: sobrescribir paths estables suele bastar.

### Rúbrica

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Job CLI | Notebook | Flags claros | Wrapper cron-ready |
| Señales | Solo prints | Exit + metrics | + log + `&&` |
| Bash | Copia a ciegas | `$?` / variables / `&&` | Orquestador `set -e` |
| Re-ejecución | Duplica / siempre 0 | Idempotente + gate | Cadena o cron verificado |
| Arquitectura | Todo mezclado | load/transform/save | + test `transform` |

---

## Cierre

> **Automatizar un data flow = CLI + señales + re-ejecución segura, operado con bash y mantenido con etapas + `transform` puro.**

**Ahora:** [`ejercicios/E4_pipeline.md`](ejercicios/E4_pipeline.md).
