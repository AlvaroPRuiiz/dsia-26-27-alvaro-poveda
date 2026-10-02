# E3 — pytest sobre el pipeline de ventas (30 min)

**Sesión:** 28 sep 2026

## Parte 0 — Calentamiento (5 min)

```bash
cd 2_pruebas_y_despliegue/ejemplos
pytest -q
# Rompe a propósito un expected y observa el diff de pytest
```

## Parte 1 — Fixture en memoria (10 min)

En el `tests/` de tu Proyecto I:

```python
@pytest.fixture
def ventas_mini():
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })
```

Escribe tests que verifiquen cuántas filas válidas/inválidas salen del validador.

## Parte 2 — Errores y bordes (8 min)

1. `pytest.raises` si el path no existe.
2. `@pytest.mark.parametrize` para precios `0`, `-1`, `1` (solo el último válido).

## Parte 3 — Integración (5 min)

Un test que lea el `ventas.csv` real del curso, marcado:

```python
@pytest.mark.integration
def test_csv_curso_tiene_140_validas_y_10_invalidas():
    ...
```

**Checkpoint del CSV del curso:** **140 válidas** y **10 inválidas**.

Ejecuta:

```bash
pytest -q
pytest -q -m "not integration"
```

## Parte 4 — Documentar (2 min)

Añade al README:

```bash
pytest -q
pytest -q -m "not integration"
```

## Hecho cuando…

≥ **8 tests** en verde y al menos 1 marcado `integration`.
