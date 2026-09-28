# Proyecto I — Programación avanzada en Python (10 %)

**Temas:** 1 (y pytest del Tema 2)  
**Presentación / arranque en clase:** 14 de septiembre de 2026  
**Entrega orientativa:** tras la sesión de pytest (**28 sep 2026**), salvo indicación distinta en aula.

## Objetivo

Desarrollar **dos** soluciones en Python que demuestren:

- Estructuras de datos adecuadas
- OOP
- Tratamiento de errores
- Validación y manipulación de datos
- **Tests unitarios con pytest**
- Buenas prácticas y documentación

**Las dos partes son obligatorias** y entran en la misma nota del Proyecto I (10 %).

---

## Parte A — Pipeline de ventas (dataset del curso)

Construye un **pipeline de calidad de datos de ventas** a partir de `Datos/ventas.csv` (o una copia en tu repo):

1. Carga y validación con excepciones de dominio.
2. Métricas de negocio (importe por región/producto, etc.).
3. CLI usable (`python -m ...`).
4. **Tests** de **todos** los módulos: `loader`, `validator`, `metrics` y `cli`.
5. README + docstrings.

Estructura orientativa (la de clase):

```text
ventas_app/
  loader.py
  validator.py
  metrics.py
  cli.py
tests/
  test_loader.py
  test_validator.py
  test_metrics.py
  test_cli.py
```

---

## Parte B — Pipeline con datos elegidos de internet

Repite el **mismo tipo de solución** (carga → validación → métricas → CLI → **tests**), pero con un **dataset público elegido por ti**.

### Requisitos del dataset

1. Debe ser **descargable o enlazable** desde internet (CSV, JSON, API pública, portal open data, Kaggle, datos.gov, etc.).
2. Indica en el README: **URL de origen**, licencia/condiciones de uso y fecha de descarga.
3. Incluye en el repo una **muestra** razonable (p. ej. miles de filas como máximo) o un script de descarga documentado; no subas ficheros enormes.
4. Define **reglas de validación propias** (nulos, rangos, tipos, duplicados, etc.) acordes al dominio elegido.
5. Calcula **al menos 3 métricas / agregaciones** con sentido para esos datos.
6. Incluye **tests** de **todos** los módulos: `loader`, `validator`, `metrics` y `cli`.

### Qué se evalúa de más en la Parte B

- Criterio al elegir y describir el dataset.
- Que el diseño no sea un copiar-pegar ciego: adaptas nombres, reglas y métricas al nuevo dominio.
- Reutilización sensata de ideas de la Parte A (módulos, excepciones, CLI, tests) sin acoplar ambos pipelines en un solo “mega-script”.

Estructura orientativa:

```text
internet_app/          # o el nombre de tu dominio
  loader.py
  validator.py
  metrics.py
  cli.py
tests/
  test_loader.py
  test_validator.py
  test_metrics.py
  test_cli.py
```

---

## Tests unitarios (obligatorio en A y B)

Referencia de clase: `2_pruebas_y_despliegue/01_pytest_intro.md` y `ejercicios/E3_pytest.md`.

### Cobertura obligatoria por módulo (A y B)

Cada parte (A y B) debe testear **los cuatro elementos**:

| Módulo | Qué debe cubrirse (mínimo) |
| --- | --- |
| **loader** | Carga correcta; path inexistente → excepción de dominio (`pytest.raises`) |
| **validator** | Filas válidas vs inválidas; bordes con `parametrize` (p. ej. 0, -1, nulos) |
| **metrics** | Al menos una agregación con resultado conocido sobre fixture en memoria |
| **cli** | Smoke test del punto de entrada (p. ej. `main` / `parse_args` / ejecución con `tmp_path` o argumentos controlados) sin depender de tu máquina |

No basta con testear solo el validator: **sin tests de loader, metrics y cli la entrega está incompleta**.

### Mínimos globales

| Requisito | Detalle |
| --- | --- |
| Cantidad | **≥ 8 tests** en total del Proyecto I (repartidos entre A y B; no todo en una sola parte) |
| Por módulo | **≥ 1 test** de `loader`, `validator`, `metrics` y `cli` en **cada** parte (A y B) |
| Cobertura de código | **≥ 60 %** sobre el código de la(s) app(s) (`ventas_app` / `internet_app` o equivalente), medida con `pytest-cov` |
| Conceptos clave | Al menos un ejemplo de **AAA + assert**, **`pytest.raises`**, **`parametrize`** y **`fixture`** |
| Unitarios | La mayoría con datos **en memoria** (fixtures) o `tmp_path`; sin red ni rutas absolutas |
| Integración | **≥ 1** test marcado `@pytest.mark.integration` (p. ej. CSV real de ventas o muestra B) |
| Ejecución | Documentada en el README |

Comandos esperados en el README:

```bash
pytest -q
pytest -q -m "not integration"
pytest --cov=ventas_app --cov=internet_app --cov-report=term-missing --cov-fail-under=60
```

> Ajusta los nombres `--cov=...` a tus paquetes reales. El umbral **60 %** es obligatorio (`--cov-fail-under=60`).

Dependencia: `pytest-cov` (añádela a tu `requirements.txt`).

**Checkpoint Parte A (CSV del curso):** el test de integración sobre `ventas.csv` debe reflejar **140 válidas** y **10 inválidas**.

Sin tests en verde de **loader + validator + metrics + cli** (en A y en B), o sin **cobertura ≥ 60 %**, el Proyecto I se considera **incompleto**.

---

## Entrega (ambas partes)

En el mismo repositorio GitHub (o carpeta del Proyecto I):

| Elemento | Parte A | Parte B |
| --- | --- | --- |
| Código modular + CLI | Obligatorio | Obligatorio |
| Tests unitarios (pytest) | Obligatorio | Obligatorio |
| README con cómo ejecutar código y tests | Obligatorio | Obligatorio (puede ser un README conjunto) |
| Datos | `ventas.csv` del curso | Muestra + URL de origen |
| Secretos / claves | No | No |

Checklist mínimo de entrega:

- [ ] Parte A ejecutable de extremo a extremo
- [ ] Parte B ejecutable de extremo a extremo
- [ ] `pytest -q` en verde (≥ 8 tests)
- [ ] Cobertura **≥ 60 %** (`--cov-fail-under=60`)
- [ ] Tests de **loader**, **validator**, **metrics** y **cli** en Parte A
- [ ] Tests de **loader**, **validator**, **metrics** y **cli** en Parte B
- [ ] ≥ 1 test `integration`
- [ ] README con comandos de ambas apps **y** de pytest (incl. coverage)
- [ ] Origen y licencia del dataset de internet documentados
- [ ] Historial Git con sentido (no un único commit gigante el último día)

---

## Rúbrica orientativa (sobre el 10 % del Proyecto I)

| Criterio | Peso | Notas |
| --- | --- | --- |
| Correctitud funcional (A + B) | 25 % | Las dos partes deben correr |
| Diseño OOP / modularidad | 20 % | Separación loader / validator / metrics / CLI |
| Manejo de errores y validación | 15 % | Reglas explícitas en ambos dominios |
| **Tests (pytest)** | **20 %** | loader+validator+metrics+cli en A y B; ≥ 8 tests; cobertura ≥ 60 %; 1 integration |
| Claridad, documentación y dataset B | 10 % | README, URL/licencia, cómo lanzar pytest + cov |
| Uso responsable de Git | 10 % | Commits legibles en ambas partes |

Si solo se entrega una de las dos partes, faltan tests de algún módulo (`loader` / `validator` / `metrics` / `cli`), o la cobertura es inferior al **60 %**, la nota del Proyecto I queda **incompleta** (no se considera entregado el proyecto).
