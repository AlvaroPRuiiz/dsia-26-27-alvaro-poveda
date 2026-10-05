# E4 — Automatizar el pipeline de ventas (50 min)

**Sesión:** 5 oct 2026  
**Referencias:** [`../01_data_flows.md`](../01_data_flows.md) (A1–A3 + B0/B4) · base [`../ejemplos/pipeline_ventas.py`](../ejemplos/pipeline_ventas.py) · datos [`../Datos/ventas.csv`](../Datos/ventas.csv)

## Meta

Dejar el demo como **job automatizable**: una máquina puede **lanzarlo** (CLI), **leer el resultado** (exit + metrics + logs) y **re-lanzarlo** sin miedo (idempotencia + gate). Además: **encadenar** un segundo/tercer script y dejar un wrapper **cron-ready**.

## Mapa → guía

| Concepto clave (Parte A) | En este ejercicio |
| --- | --- |
| A1 — Job CLI parametrizado | Partes 0–1 |
| A2 — Señales (exit / metrics / logs) | Partes 2–3 |
| A3 — Idempotencia + gate | Parte 4 |
| B0 — Etapas + `transform` puro | Parte 7 |
| B4 — Encadenación + cron | Partes 5–6 |

## Parte 0 — Orientación (3 min)

Abre [`../01_data_flows.md`](../01_data_flows.md) y copia en una frase la **regla de oro** de la sesión.

Dibuja en 4 cajas las etapas del demo:

```text
load → transform → save → señales (log + metrics + exit)
```

## Parte 1 — A1: job CLI (parametrizar sin tocar código) (5 min)

```bash
cd 3_automatizacion_e_ia

# Política holgada
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_dev \
  --max-error-rate 0.5
echo "dev_exit=$?"

# Misma lógica, otra política (sin editar el .py)
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_prod \
  --max-error-rate 0.05
echo "prod_exit=$?"
```

Escribe: *¿qué cambió entre ambas corridas y qué no?* (flags vs código).

## Parte 2 — A2: señales + contrato de esquema (8 min)

### 2.1 Exit codes del curso

| Código | Cuándo |
| --- | --- |
| `0` | OK: artefactos escritos |
| `1` | Gate de calidad (`error_rate` alto) |
| `2` | Input inválido (path / columnas) |

### 2.2 Forzar exit `2` (contrato)

Columnas mínimas: `fecha, region, producto, unidades, precio_unitario, cliente_id`.

```bash
# Genera un CSV roto (sin region)
python - <<'PY'
import pandas as pd
df = pd.read_csv("Datos/ventas.csv")
df.drop(columns=["region"]).to_csv("/tmp/ventas_roto.csv", index=False)
PY

python ejemplos/pipeline_ventas.py \
  --input /tmp/ventas_roto.csv \
  --output-dir /tmp/out_bad \
  --max-error-rate 0.5
echo "exit=$?"   # esperado: 2
```

Si el demo aún no aborta con `2` ante columnas faltantes, **impléméntalo** (log ERROR + `return 2` / `sys.exit(2)` sin escribir limpio).

### 2.3 Leer señales en una corrida OK

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_ok \
  --max-error-rate 0.5
echo "exit=$?"
cat /tmp/ventas_ok/metrics.json
tail -n 20 /tmp/ventas_ok/run.log
```

`metrics.json` debe incluir al menos: `rows_in`, `rows_out`, `rows_dropped`, `error_rate`, `importe_total`.  
Log en **consola y** `run.log`.

## Parte 3 — Composición con `&&` (4 min)

La señal gobierna el siguiente paso:

```bash
OUT=/tmp/pub_demo
PUB=/tmp/pub_demo/publicado

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5 \
&& mkdir -p "$PUB" \
&& cp "$OUT/ventas_limpias.csv" "$PUB/" \
&& cp "$OUT/metrics.json" "$PUB/" \
&& echo "Publicado en $PUB"

# Ahora con umbral imposible de cumplir → no debe publicar
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/no_pub --max-error-rate 0.05 \
&& mkdir -p /tmp/no_pub/publicado \
&& cp /tmp/no_pub/ventas_limpias.csv /tmp/no_pub/publicado/ \
|| echo "KO: cadena detenida (esperado)"
ls /tmp/no_pub/publicado 2>/dev/null || echo "(no hay publicado — bien)"
```

## Parte 4 — A3: gate + idempotencia (8 min)

### 4.1 Gate / fail-fast

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out_gate \
  --max-error-rate 0.05
echo "exit=$?"   # esperado: 1
```

**Checkpoint:** ~**140 válidas / 10 inválidas** → `error_rate ≈ 0.067`.  
Si `error_rate > max-error-rate` → **no** `save` del limpio; exit `1`.

### 4.2 Idempotencia

```bash
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem
```

Esperado: `ventas_limpias.csv`, `metrics.json`, `run.log` — **una vez** cada uno (sobrescribe, no duplica).

En una frase: *¿por qué cron exige idempotencia + exit codes?*

## Parte 5 — Encadenación de scripts (10 min)

Implementa el patrón de la guía (B4.1): **limpiar → validar metrics → notificar**.

### 5.1 `ejemplos/check_metrics.py`

CLI que lee `metrics.json` y sale `1` si no cumple umbrales (`--max-error-rate`, `--min-rows-out`). Puedes partir del stub de la guía.

### 5.2 `ejemplos/notify_ok.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
stamp="${1:-$(date -Iseconds)}"
mkdir -p Datos/salida
echo "PIPELINE_OK ${stamp}" | tee "Datos/salida/LAST_OK.txt"
```

```bash
chmod +x ejemplos/notify_ok.sh
```

### 5.3 Orquestador `scripts/run_cadena_ventas.sh`

Con `set -euo pipefail`:

1. `pipeline_ventas.py` → `$OUT`  
2. `check_metrics.py --metrics $OUT/metrics.json ...`  
3. `notify_ok.sh` **solo** si 1 y 2 fueron `0`

```bash
mkdir -p scripts
chmod +x scripts/run_cadena_ventas.sh
./scripts/run_cadena_ventas.sh
echo "exit=$?"
cat Datos/salida/LAST_OK.txt
```

Prueba negativa: cambia temporalmente `--min-rows-out` a `999999` en el orquestador y confirma que **no** se escribe un nuevo éxito engañoso (o que el paso 3 no corre).

## Parte 6 — Wrapper cron-ready (7 min)

Crea `scripts/run_pipeline_ventas.sh` al estilo B4.2:

- paths **absolutos** (o `REPO` derivado del script),
- `set -euo pipefail`,
- activa tu venv si aplica,
- `--output-dir` con fecha (`$(date +%F)`),
- redirige stdout/stderr a `Datos/salida/cron_logs/ventas_FECHA.log`.

```bash
chmod +x scripts/run_pipeline_ventas.sh
./scripts/run_pipeline_ventas.sh
echo "exit=$?"
tail -n 30 Datos/salida/cron_logs/ventas_$(date +%F).log
```

Escribe (no hace falta instalarlo) la línea de crontab que lo lanzaría cada día a las 02:15:

```cron
15 2 * * * /ruta/absoluta/.../scripts/run_pipeline_ventas.sh
```

Opcional: `crontab -e` en tu máquina. En clase basta el wrapper + la línea anotada.

## Parte 7 — B0: `transform` puro + test (5 min)

Sin tocar disco ni el CSV del curso:

```python
def test_transform_report_counts():
    df = pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })
    clean, report = transform(df)
    assert report["rows_in"] == 3
    assert report["rows_dropped"] == 2
    assert report["rows_out"] == 1
```

Ejecuta el test (pytest en tu carpeta de práctica o `python -c` con asserts).  
Recuerda: automatizar el job (A1–A3) **y** poder testear el núcleo son complementarios.

## Hecho cuando…

### Conceptos clave

- [ ] A1: lanzo el job solo con flags; cambio umbral sin editar código
- [ ] A2: distingo exit `0` / `1` / `2`; leo `metrics.json` + `run.log`
- [ ] A3: gate `0.05` → exit `1`; re-run idempotente en el mismo `output-dir`

### Composición / operación

- [ ] `&&` no publica si el pipeline falla
- [ ] Cadena `pipeline → check_metrics → notify` con `set -e`
- [ ] Wrapper cron-ready + línea de crontab anotada

### Arquitectura

- [ ] Sé nombrar las etapas load/transform/save/señales
- [ ] Test de `transform` en memoria en verde

### Frases cortas (escríbelas)

- [ ] CLI ≠ notebook  
- [ ] Exit codes = señales para máquinas  
- [ ] Idempotencia + gate = seguro de re-ejecutar  
