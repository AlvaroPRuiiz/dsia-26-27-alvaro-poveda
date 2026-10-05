# E4 — Automatizar el pipeline de ventas (50 min)

**Sesión:** 5 oct 2026  
**Guía:** [`../01_data_flows.md`](../01_data_flows.md) · **Demo:** [`../ejemplos/pipeline_ventas.py`](../ejemplos/pipeline_ventas.py) · **Datos:** [`../Datos/ventas.csv`](../Datos/ventas.csv)

## Meta

Dejar el flujo como un **job que puede correr solo**:

```text
lanzar (CLI) → señalizar (exit + metrics + log) → re-lanzar (idempotencia + gate)
                         ↓
              operar con bash (&&, cadena, cron-ready)
```

**Núcleo (obligatorio, ~30 min):** Partes 1–4.  
**Extensión (deseable, ~20 min):** Partes 5–7.

| Guía | Ejercicio |
| --- | --- |
| A1 CLI | Parte 1 |
| A2 señales | Partes 2–3 |
| A3 idem + gate | Parte 4 |
| B3–B5 bash / cadena / cron | Partes 5–6 |
| B2 `transform` puro | Parte 7 |

---

## Parte 1 — A1: lanzar con flags (5 min)

```bash
cd 3_automatizacion_e_ia

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_dev \
  --max-error-rate 0.5
echo "dev_exit=$?"
ls /tmp/ventas_dev
```

Sin editar el `.py`, cambia solo el umbral:

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_prod \
  --max-error-rate 0.05
echo "prod_exit=$?"   # esperado: 1
```

Anota en una línea: *qué cambió (flags) y qué no (código)*.

---

## Parte 2 — A2: señales (8 min)

| Exit | Significado |
| --- | --- |
| `0` | OK: artefactos escritos |
| `1` | Gate de calidad |
| `2` | Input inválido (path / columnas) |

### 2.1 Leer evidencia (ejecución OK)

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_ok \
  --max-error-rate 0.5
echo "exit=$?"
cat /tmp/ventas_ok/metrics.json
tail -n 20 /tmp/ventas_ok/run.log
```

Comprueba campos: `rows_in`, `rows_out`, `rows_dropped`, `error_rate`, `importe_total`.  
Log en consola **y** `run.log`.

### 2.2 Forzar exit `2` (contrato de columnas)

```bash
python - <<'PY'
import pandas as pd
pd.read_csv("Datos/ventas.csv").drop(columns=["region"]).to_csv("/tmp/ventas_roto.csv", index=False)
PY

python ejemplos/pipeline_ventas.py \
  --input /tmp/ventas_roto.csv \
  --output-dir /tmp/out_bad \
  --max-error-rate 0.5
echo "exit=$?"   # esperado: 2
```

El demo del curso ya debe hacerlo. Si en **tu** copia no: log ERROR + `return 2` sin escribir limpio.

---

## Parte 3 — Bash: la señal gobierna el siguiente paso (5 min)

```bash
OUT=/tmp/pub_demo
PUB="$OUT/publicado"

python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5 \
&& mkdir -p "$PUB" \
&& cp "$OUT/ventas_limpias.csv" "$OUT/metrics.json" "$PUB/" \
&& echo "Publicado en $PUB"

# Gate rojo → no debe publicar
rm -rf /tmp/no_pub
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/no_pub --max-error-rate 0.05 \
&& mkdir -p /tmp/no_pub/publicado \
&& cp /tmp/no_pub/ventas_limpias.csv /tmp/no_pub/publicado/ \
|| echo "KO: cadena detenida (esperado)"
test ! -d /tmp/no_pub/publicado && echo "bien: no hay publicado"
```

Conceptos bash que usas: `"$OUT"`, `&&`, `||`, `mkdir -p`, `echo $?` (Parte 1–2).

---

## Parte 4 — A3: gate + idempotencia (7 min)

**Checkpoint CSV:** ~140 válidas / 10 inválidas → `error_rate ≈ 0.067`.

```bash
# Gate: no tratar como éxito una corrida mala
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir /tmp/out_gate --max-error-rate 0.05
echo "exit=$?"   # 1 — y sin “aprobar” la corrida

# Idempotencia: mismo destino dos veces
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem
# Esperado: ventas_limpias.csv, metrics.json, run.log (una vez cada uno)
```

Frase: *¿por qué cron exige idempotencia + exit codes?*

> **Núcleo A1–A3 listo.** Si vas justos de tiempo, salta a la checklist y deja 5–7 como deberes / Proyecto II.

---

## Parte 5 — Encadenar scripts (10 min) · B4

Patrón: **limpiar → validar metrics → notificar** (el 3.º solo si 1 y 2 salen `0`).

### 5.1 Crea `ejemplos/check_metrics.py`

Puedes copiar el stub de la guía (B4). Debe aceptar `--metrics`, `--max-error-rate`, `--min-rows-out` y devolver exit `1` si no cumple.

### 5.2 Crea `ejemplos/notify_ok.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
mkdir -p Datos/salida
echo "PIPELINE_OK ${1:-$(date -Iseconds)}" | tee Datos/salida/LAST_OK.txt
```

### 5.3 Crea `scripts/run_cadena_ventas.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
OUT="Datos/salida/$(date +%F)"
mkdir -p "$OUT"

echo "== 1/3 limpiar =="
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv --output-dir "$OUT" --max-error-rate 0.5

echo "== 2/3 metrics =="
python ejemplos/check_metrics.py \
  --metrics "$OUT/metrics.json" --max-error-rate 0.1 --min-rows-out 100

echo "== 3/3 notify =="
bash ejemplos/notify_ok.sh "$(date +%F)"
echo "Cadena OK → $OUT"
```

```bash
chmod +x ejemplos/notify_ok.sh scripts/run_cadena_ventas.sh
./scripts/run_cadena_ventas.sh
echo "exit=$?"
cat Datos/salida/LAST_OK.txt
```

Prueba negativa: `--min-rows-out 999999` en el paso 2 → el paso 3 **no** debe correr (`set -e`).

---

## Parte 6 — Wrapper cron-ready (7 min) · B5

Crea `scripts/run_pipeline_ventas.sh` (plantilla en la guía B5):

- `set -euo pipefail`
- `REPO` absoluto o derivado de `"$0"`
- venv si lo usas
- `--output-dir` con `$(date +%F)`
- `>> …/cron_logs/ventas_FECHA.log 2>&1`

```bash
chmod +x scripts/run_pipeline_ventas.sh
./scripts/run_pipeline_ventas.sh
echo "exit=$?"
tail -n 30 Datos/salida/cron_logs/ventas_$(date +%F).log
```

Anota la línea de crontab (no hace falta instalarla):

```cron
15 2 * * * /ruta/absoluta/.../scripts/run_pipeline_ventas.sh
```

---

## Parte 7 — `transform` puro (5 min) · B2

```python
def test_transform_report_counts():
    import pandas as pd
    from pipeline_ventas import transform  # ajusta el import a tu layout

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

Automatizar el job (A1–A3) y testear el núcleo son complementarios: uno opera solo; el otro se mantiene.

---

## Hecho cuando…

### Núcleo (A1–A3)

- [ ] Lanzo con flags; cambio umbral sin editar código  
- [ ] Distingo exit `0` / `1` / `2`; leo `metrics.json` + `run.log`  
- [ ] `&&` no publica si el pipeline falla  
- [ ] Gate `0.05` → exit `1`; re-run idempotente  

### Extensión

- [ ] Cadena `pipeline → check_metrics → notify` con `set -e`  
- [ ] Wrapper cron-ready + línea de crontab anotada  
- [ ] Test de `transform` en memoria  

### Tres frases

- [ ] CLI ≠ notebook  
- [ ] Exit / metrics / log = señales para máquinas  
- [ ] Idempotencia + gate = seguro de re-ejecutar  
