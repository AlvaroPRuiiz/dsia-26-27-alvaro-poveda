# Sesión 28 sep 2026 — pytest, test suites y aserciones

| Recurso | Fichero |
| --- | --- |
| Demo (`calculator`) | [`ejemplos/`](ejemplos/) |
| Ejercicio de clase | [`ejercicios/E3_pytest.md`](ejercicios/E3_pytest.md) |
| CI del repo | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |

Este documento es la **referencia amplia** de la sesión de tests: por qué testear en DSIA, los **tres conceptos clave** que debes dominar al salir de clase, y material suplementario (pirámide, CI, marcas, anti-patrones, chuleta) para el Proyecto I y el resto del curso.

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar la sesión **debes** ser capaz de:

1. Escribir un test unitario con patrón **AAA** y `assert`.
2. Probar errores y bordes con **`pytest.raises`** y **`@pytest.mark.parametrize`**.
3. Reutilizar datos de prueba con **`@pytest.fixture`** (sin depender de ficheros reales en los unitarios).

### Deseables (material suplementario)

4. Distinguir tests unitarios, de integración y E2E (pirámide).
5. Marcar integración (`@pytest.mark.integration`) y filtrar con `-m`.
6. Entender qué hace el workflow de CI del curso.
7. Llevar ≥ 8 tests al validador del Proyecto I.

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos

En DSIA no entregamos “código que me funciona a mí ahora”. Entregamos soluciones que otra persona (o CI) pueda:

1. clonar,
2. instalar,
3. ejecutar,
4. **verificar automáticamente** con `pytest`.

Sin tests, cada refactor del pipeline o del cliente de IA es un salto de fe.

### 1.2 Mapa mental del semestre

```text
Sesión 1  →  venv + Git
Sesión 2  →  pandas
Sesión 3  →  arquitectura / SOLID
Sesión 4  →  pytest (hoy)          ← convierte el diseño en confianza
Después   →  pipelines, APIs IA, E2E, deploy
```

La arquitectura de la sesión anterior **habilita** los tests: etapas puras + I/O en los bordes.

### 1.3 Analogías útiles

| Concepto | Analogía |
| --- | --- |
| Test unitario | Probar una bombilla fuera del edificio |
| Integración | Probar que el interruptor enciende la bombilla |
| E2E | Recorrer la casa entera con un checklist |
| `assert` | “Espero que esto sea verdad” |
| `raises` | “Espero que esto falle de esta forma” |
| `parametrize` | Misma pregunta, muchos datos |
| `fixture` | Bandeja de ingredientes preparados para varios platos |
| CI | El portero que no deja pasar un PR roto |

### 1.4 Regla de oro

> **Si no puedes testearlo sin red, sin tu portátil y sin “Run All”, aún no está lo bastante modular.**

---

# PARTE A — Tres conceptos clave (obligatorio)

> Prioridad de clase: domina A1 → A2 → A3. El resto del documento es red de seguridad y profundidad.

---

## A1. Concepto clave 1 — AAA + `assert` (el test unitario mínimo)

### Qué es

Un **test unitario** comprueba una unidad pequeña (función/método) de forma **determinista**.

Patrón **AAA**:

1. **Arrange** — prepara datos/estado.
2. **Act** — llama a la unidad.
3. **Assert** — comprueba el resultado.

### Demo del curso

```bash
cd 2_pruebas_y_despliegue/ejemplos
pytest -q
pytest -vv
```

```python
from calculator import add


def test_add():
    # Arrange
    a, b = 2, 3
    # Act
    result = add(a, b)
    # Assert
    assert result == 5
```

Equivalente compacto (válido cuando es obvio):

```python
def test_add():
    assert add(2, 3) == 5
```

### Por qué importa en DSIA

Tu `validar_ventas` / `total_by_region` deben poder testearse **sin** abrir Excel ni llamar a OpenAI.

### Checklist del concepto 1

- [ ] Sé escribir `def test_...():` con `assert`
- [ ] Sé explicar Arrange / Act / Assert en una frase
- [ ] Sé lanzar `pytest -q` desde `ejemplos/`

---

## A2. Concepto clave 2 — `raises` + `parametrize` (errores y bordes)

### 2.1 Esperar un error: `pytest.raises`

Cuando la unidad **debe** fallar (path inexistente, división por cero, precio inválido):

```python
import pytest
from calculator import divide


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

Ejecuta solo ese test:

```bash
pytest -q test_calculator.py::test_divide_by_zero_raises
```

### 2.2 Varios casos, un solo test: `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize(
    ("value", "low", "high", "expected"),
    [
        (5, 0, 10, 5),
        (-1, 0, 10, 0),
        (99, 0, 10, 10),
    ],
)
def test_clamp(value, low, high, expected):
    assert clamp(value, low, high) == expected
```

Para el validador de ventas:

```python
@pytest.mark.parametrize("precio", [0, -1])
def test_precio_no_positivo_es_error(precio, ventas_mini_factory):
    ...
```

### Por qué importa en DSIA

Los bugs caros viven en los **bordes**: nulos, ceros, negativos, ficheros que no existen. Si solo testeas el “camino feliz”, CI te dará falsa seguridad.

### Checklist del concepto 2

- [ ] Sé usar `with pytest.raises(...):`
- [ ] Sé parametrizar al menos 2–3 casos
- [ ] Sé localizar un test con `pytest path::test_name`

---

## A3. Concepto clave 3 — `fixture` (datos reutilizables y aislamiento)

### Qué es

Una **fixture** prepara contexto (DataFrame, path temporal, objeto) y lo inyecta en los tests que lo pidan por nombre.

```python
import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "unidades": [1, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
    })


def test_validador_separa_invalidos(sample_df):
    validos, errores = validar_ventas(sample_df)
    assert len(validos) == 1
    assert len(errores) == 2
```

### Reglas prácticas

1. Los **unitarios** prefieren DataFrames **en memoria** (fixture), no el CSV grande del curso.
2. Si necesitas disco: `tmp_path` (suplementario, sección B).
3. No compartas estado mutable entre tests sin control (cada test debe poder correr solo).

### Por qué importa en DSIA

Sin fixtures, copias el mismo `DataFrame(...)` en 8 tests y el día que cambias una columna rompes todo a mano. Con fixture, cambias **un** sitio.

### Checklist del concepto 3

- [ ] Sé definir `@pytest.fixture`
- [ ] Sé inyectarla como argumento del test
- [ ] Sé explicar por qué el unitario no debería depender de internet ni de tu Desktop

---

## A4. Mapa mental de los 3 conceptos

```text
AAA + assert     →  “¿la función hace lo correcto?”
raises + params  →  “¿falla donde debe? ¿y en varios bordes?”
fixture          →  “¿reutilizo datos limpios sin copiar-pegar?”
```

Si dominas eso, puedes hacer el E3 y el mínimo del Proyecto I.

**Siguiente paso inmediato en clase:** [`ejercicios/E3_pytest.md`](ejercicios/E3_pytest.md).

---

# PARTE B — Material suplementario

> Úsalo para profundizar, preparar CI/Proyecto I y resolver dudas. **No** sustituye a A1–A3.

---

## B1. Pirámide de tests (contexto)

```text
        /\
       /E2E\         pocos, lentos, frágiles
      /------\
     / integ. \      algunos (CSV real, API mock)
    /----------\
   /  unitarios \    muchos, rápidos, baratos
  /--------------\
```

| Tipo | Qué prueba | Ejemplo DSIA |
| --- | --- | --- |
| Unitario | Función pura / regla | `validar_ventas(df_mini)` |
| Integración | Piezas + I/O real acotado | leer `Datos/ventas.csv` |
| E2E | Flujo completo | CLI → API → `/health` (más adelante) |

**Heurística:** la mayoría de tus tests del Proyecto I deben ser unitarios.

---

## B2. Anatomía del demo `ejemplos/`

### B2.1 Código bajo prueba — `calculator.py`

- `add` — camino feliz.
- `divide` — error explícito si `b == 0`.
- `clamp` — bordes + `ValueError` si `low > high`.

### B2.2 Tests — `test_calculator.py`

Cubre los 3 conceptos clave:

| Test | Concepto |
| --- | --- |
| `test_add` / `test_divide` | AAA + assert |
| `test_divide_by_zero_raises` / `test_clamp_invalid_bounds` | `raises` |
| `test_clamp` parametrizado | `parametrize` |

### B2.3 Guion de exposición (30 min)

1. Pirámide en 5 min (esta sección B1).  
2. AAA sobre `add` / `divide` (concepto A1).  
3. `raises` + `parametrize` en vivo (concepto A2).  
4. Fixture mental hacia ventas + abrir CI (concepto A3 + B4).

---

## B3. Buenas prácticas de nombres y organización

### Nombres

Patrón recomendado:

```text
test_<unidad>_<escenario>_<resultado>
```

Ejemplos:

- `test_validar_ventas_precio_negativo_va_a_errores`
- `test_load_path_inexistente_raises_dataloadererror`

### Estructura en el Proyecto I

```text
ventas_app/
  loader.py
  validator.py
  metrics.py
  cli.py
tests/
  test_validator.py
  test_loader.py
  test_metrics.py
```

pytest descubre ficheros `test_*.py` y funciones `test_*`.

---

## B4. Marcas, integración y filtrado

```python
@pytest.mark.integration
def test_csv_curso_checkpoint():
    ...
```

```bash
pytest -q                 # todos
pytest -q -m "not integration"   # solo unitarios (ideal en bucle local)
pytest -q -m integration         # solo integración
```

Registra marcas en `pytest.ini` o `pyproject.toml` si pytest avisa de marcas desconocidas (cuando configures tu repo).

**Para el CSV del curso:** el checkpoint actual de `ventas.csv` es **140 válidas / 10 inválidas** (no uses números viejos de material anterior).

---

## B5. `tmp_path` (ficheros sin ensuciar el repo)

```python
def test_load_csv_ok(tmp_path):
    p = tmp_path / "mini.csv"
    p.write_text("unidades,precio_unitario\n1,10\n", encoding="utf-8")
    df = load(p)
    assert len(df) == 1
```

Útil para el loader sin tocar `Datos/`.

---

## B6. CI del curso (gate de merge)

Abre [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

Idea:

```text
push / PR → instalar deps → pytest → (pasa o bloquea)
```

Tu README del proyecto debería documentar:

```bash
pytest -q
pytest -q -m "not integration"
```

Sin esa línea, el compañero (y el profesor) no saben cómo verificar.

---

## B7. Anti-patrones frecuentes (lista negra)

1. Tests que dependen del orden de ejecución.
2. Tests que necesitan internet “porque sí”.
3. Un solo test gigante que lo prueba todo.
4. `assert True` / tests sin aserción real.
5. Capturar `Exception` en producción y no testear el error concreto.
6. Leer el CSV completo del curso en **todos** los unitarios.
7. Hardcodear rutas `/Users/yo/...` en tests.
8. Cambiar código de producción solo para “hacer pasar” el test sin entender el fallo.
9. No fijar datos de ejemplo (flaky tests).
10. Celebrar coverage alto con tests que no asertan nada útil.

---

## B8. Puente al Proyecto I (y al II)

### Proyecto I

- ≥ **8 tests** en verde sobre el pipeline (loader/validator/metrics).
- Al menos 1 marcado `integration` (CSV real).
- Fixtures en memoria para el grueso.

### Proyecto II (adelanto)

- Tests del entrenamiento/inferencia sklearn (fixture de modelo pequeño o `tmp_path`).
- Tests del cliente IA con **mock** (no llamar a la API real en CI).

La arquitectura (Protocol / Strategy) existe en gran parte **para poder testear**.

---

## B9. Ejemplo guiado: del validador al test

### Código (idea)

```python
def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
    work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")
    ok = (
        work["unidades"].notna() & (work["unidades"] > 0)
        & work["precio_unitario"].notna() & (work["precio_unitario"] > 0)
    )
    validos = work.loc[ok].copy()
    errores = work.loc[~ok].copy()
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]
    return validos, errores
```

### Test (los 3 conceptos juntos)

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


def test_validar_ventas_cuenta_validos_e_invalidos(ventas_mini):
    validos, errores = validar_ventas(ventas_mini)
    assert len(validos) == 1
    assert len(errores) == 2


@pytest.mark.parametrize("precio", [0, -1])
def test_precio_no_positivo_no_es_valido(precio):
    df = pd.DataFrame({"unidades": [1], "precio_unitario": [precio]})
    validos, errores = validar_ventas(df)
    assert len(validos) == 0
    assert len(errores) == 1
```

---

## B10. Autoevaluación (clave vs suplementario)

### Clave (debe salir fluido)

1. ¿Qué es AAA?
2. ¿Cómo pruebas que una función lanza `ValueError`?
3. ¿Para qué sirve `parametrize`?
4. ¿Qué problema resuelve una fixture?

### Suplementario

5. ¿Unitario vs integración en una frase?
6. ¿Qué ejecuta `pytest -m "not integration"`?
7. ¿Por qué CI necesita tests deterministas?

Si fallas en 1–4, rehaz la Parte A y el demo `ejemplos/` antes del E3.

---

## B11. Checklist de salida

### Conceptos clave

- [ ] AAA + `assert` escrito por ti  
- [ ] Un `pytest.raises` en verde  
- [ ] Un `parametrize` en verde  
- [ ] Una fixture usada por ≥ 2 tests  

### Ejercicio / proyecto

- [ ] E3 completado  
- [ ] ≥ 8 tests en el Proyecto I  
- [ ] ≥ 1 test `integration`  
- [ ] README con comandos `pytest`  

---

## B12. Para la siguiente sesión

1. Deja los tests del Proyecto I en verde en tu máquina.  
2. No rompas la separación loader / validator / metrics: es lo que hace baratos los unitarios.  
3. Cuando lleguen pipelines y APIs, añade mocks y marcas de integración con el mismo criterio.

---

## B13. Apéndice A — Chuleta rápida

```bash
cd 2_pruebas_y_despliegue/ejemplos
pytest -q
pytest -vv
pytest -q test_calculator.py::test_divide_by_zero_raises
pytest -q -m "not integration"
```

```python
def test_ok():
    assert f(1) == 2

def test_error():
    with pytest.raises(ValueError):
        f(-1)

@pytest.mark.parametrize("x, expected", [(0, 0), (1, 1)])
def test_many(x, expected):
    assert f(x) == expected

@pytest.fixture
def sample_df():
    return pd.DataFrame({"unidades": [1, None], "precio_unitario": [10, 5]})
```

---

## B14. Apéndice B — Glosario corto EN/ES

| EN | ES / nota |
| --- | --- |
| unit test | prueba unitaria |
| integration test | prueba de integración |
| assertion | aserción / comprobación |
| fixture | fijación / datos preparados |
| parametrize | parametrizar casos |
| test suite | batería de tests |
| flaky test | test inestable |
| continuous integration (CI) | integración continua |

---

## B15. Apéndice C — Preguntas típicas de clase

**¿Obligatorio pytest o vale unittest?**  
En DSIA usamos **pytest** (más ergonómico: assert plano, fixtures, parametrize).

**¿Cuántos tests son suficientes?**  
En Proyecto I: mínimo **8** con sentido. Calidad > cantidad.

**¿Debo testear el CLI?**  
Primero validator/metrics/loader. El CLI puede tener 1 smoke test más adelante.

**¿Los tests van en el mismo fichero que el código?**  
No. Carpeta `tests/` separada.

**¿Puedo usar el CSV real en todos los tests?**  
No. CSV real → integración. Unitarios → fixture en memoria.

**¿Qué hago si CI falla y en local pasa?**  
Versiones, cwd, marcas, ficheros no commiteados, o test flaky. Reproduce con el mismo comando que CI.

---

## B16. Apéndice D — Mini rúbrica de autocontrol (tests)

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Conceptos clave | Solo `assert` suelto | AAA + raises + fixture | + parametrize sistemático |
| Aislamiento | Depende de red/rutas propias | Fixtures en memoria | + `tmp_path` / marcas |
| Bordes | Solo camino feliz | Errores tipados | Matriz de bordes clara |
| Proyecto I | < 8 tests | ≥ 8 + 1 integration | README + CI local documentado |

---

## 25. Cierre

Si dominas la **Parte A**, tienes lo esencial de la sesión:

> **AAA + bordes (`raises`/`parametrize`) + fixtures = tests útiles para un pipeline de datos.**

El material suplementario (pirámide, CI, marcas) te prepara para que esos tests vivan en el repo y en el merge.

**Siguiente paso inmediato:** haz [`ejercicios/E3_pytest.md`](ejercicios/E3_pytest.md) y conecta los 3 conceptos a tu `ventas_app/`.
