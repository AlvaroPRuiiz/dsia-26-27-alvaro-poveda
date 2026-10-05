# E4 — Pipeline de datos robusto (35 min)

**Sesión:** 5 oct 2026  
**Referencias:** [`../01_data_flows.md`](../01_data_flows.md) · base [`../ejemplos/pipeline_ventas.py`](../ejemplos/pipeline_ventas.py) · datos [`../Datos/ventas.csv`](../Datos/ventas.csv)

## Meta

Convertir el demo en un **job automatizable**: contrato de entrada, gate de calidad, observabilidad, exit codes útiles para scripts/CI, e **idempotencia** al re-ejecutar. El núcleo (`transform`) debe seguir siendo testeable sin disco.

## Conceptos de automatización que practicas

| Concepto | Qué harás |
| --- | --- |
| Job ≠ notebook | Lanzar por CLI con flags; sin “Run All” |
| Contrato de esquema | Abortar si faltan columnas |
| Fail-fast / gate | No publicar si `error_rate` supera el umbral |
| Exit codes | `0` OK · `1` calidad · `2` input inválido |
| Observabilidad | Consola + `run.log` + `metrics.json` |
| Idempotencia | Re-ejecutar sobre el mismo `output-dir` sin duplicar basura |
| Separación I/O vs puro | Test de `transform` en memoria |

## Parte 0 — Smoke del job (3 min)

```bash
cd 3_automatizacion_e_ia
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/ventas_out \
  --max-error-rate 0.5
echo "exit=$?"
ls /tmp/ventas_out
```

Anota qué artefactos salen y confirma `exit=0`.

## Parte 1 — Contrato de columnas (7 min)

Antes de transformar, el `load` debe verificar columnas mínimas:

`fecha, region, producto, unidades, precio_unitario, cliente_id`

Si falta alguna → log **ERROR** + exit code **`2`** (no escribas CSV “limpio”).

Prueba rápida (rompe el contrato a propósito):

```bash
# CSV sin columna region → debe salir con código 2
python ejemplos/pipeline_ventas.py \
  --input /tmp/ventas_roto.csv \
  --output-dir /tmp/out_bad \
  --max-error-rate 0.5
echo "exit=$?"   # esperado: 2
```

(Puedes generar `/tmp/ventas_roto.csv` quitando una columna del CSV del curso.)

## Parte 2 — Umbral de calidad / fail-fast (7 min)

Asegura `--max-error-rate` (float, default `0.5`).

Si `rows_dropped / rows_in > max_error_rate` → **no** llames a `save`; exit code **`1`**.

```bash
python ejemplos/pipeline_ventas.py \
  --input Datos/ventas.csv \
  --output-dir /tmp/out_gate \
  --max-error-rate 0.05
echo "exit=$?"   # esperado: 1 (10/150 ≈ 0.067)
```

**Checkpoint del CSV del curso:** ~**140 válidas / 10 inválidas**.

## Parte 3 — Observabilidad (7 min)

Automatizar sin telemetría es volar a ciegas. Debe existir:

1. Log a **consola** y a `output-dir/run.log` (misma traza).  
2. `output-dir/metrics.json` con al menos: `rows_in`, `rows_out`, `rows_dropped`, `error_rate`, `importe_total`.

Tras una corrida OK (`--max-error-rate 0.5`):

```bash
cat /tmp/ventas_out/metrics.json
tail -n 20 /tmp/ventas_out/run.log
```

## Parte 4 — Idempotencia (5 min)

Un job automatizado se **re-ejecuta**. Comprueba:

1. Lanza dos veces el mismo comando sobre el **mismo** `--output-dir`.  
2. No deben aparecer ficheros duplicados tipo `ventas_limpias (1).csv`.  
3. `metrics.json` / `ventas_limpias.csv` se **sobrescriben** de forma predecible.

```bash
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
python ejemplos/pipeline_ventas.py --input Datos/ventas.csv --output-dir /tmp/idem --max-error-rate 0.5
ls /tmp/idem   # solo los artefactos esperados, una vez cada uno
```

Escribe en una frase: *¿por qué la idempotencia importa si esto lo lanza cron o CI?*

## Parte 5 — Test puro de `transform` (6 min)

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

Esto es automatización de **calidad del código**: el núcleo se valida en CI sin I/O.

## Hecho cuando…

- [ ] Contrato de columnas → exit `2` si falla
- [ ] Umbral `0.05` → exit `1` con el CSV del curso
- [ ] Existen `run.log` + `metrics.json` en una corrida OK
- [ ] Re-ejecutar el mismo `output-dir` es idempotente (sobrescribe, no duplica)
- [ ] Test de `transform` en memoria en verde
- [ ] Sabes explicar fail-fast, observabilidad e idempotencia en una frase cada uno
