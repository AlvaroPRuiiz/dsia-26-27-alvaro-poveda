# Sesión 28 sep 2026 — CI con GitHub Actions (validar el código)

| Recurso | Fichero |
| --- | --- |
| Plantilla de workflow | [`ejemplos/ci_proyecto_i.yml`](ejemplos/ci_proyecto_i.yml) |
| Ejercicio de clase | [`ejercicios/E4_ci_github.md`](ejercicios/E4_ci_github.md) |
| CI del repo del curso | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| Base previa (pytest) | [`01_pytest_intro.md`](01_pytest_intro.md) |

Este documento es la **referencia amplia** de integración continua (CI) en DSIA: por qué automatizar la validación del código, los **tres conceptos clave** que debes dominar, y material suplementario para dejar el **Proyecto I** con un workflow verde en GitHub Actions.

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar **debes** ser capaz de:

1. Explicar qué es **CI** y por qué un push/PR debe **validar automáticamente** el código.
2. Leer y adaptar un **workflow de GitHub Actions** (triggers → job → steps: checkout, Python, install, pytest).
3. Configurar CI en **tu repo del Proyecto I** para que falle si los tests o la **cobertura &lt; 60 %** no cumplen.

### Deseables (material suplementario)

4. Distinguir CI local (`pytest`) vs CI remoto (Actions).
5. Interpretar logs rojos en la pestaña Actions.
6. Añadir un badge de estado al README.
7. Evitar secretos y rutas absolutas en el workflow.

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos

En DSIA no basta con “en mi portátil pasa pytest”. Entregamos un repo donde **GitHub comprueba** por ti:

```text
push / pull request → Actions instala deps → pytest (+ coverage) → verde o rojo
```

Eso es el mismo espíritu del resto del curso: reproducible, revisable, listo para crecer al Proyecto II/III.

### 1.2 Mapa mental

```text
pytest (01)     →  sabes escribir tests
CI (02, hoy)    →  esos tests se ejecutan solos en cada cambio
Proyecto I      →  gate: tests + cov ≥ 60 % + módulos cubiertos
Proyecto II/III →  CI sigue siendo la red de seguridad (mock IA, sklearn, API)
```

### 1.3 Analogías

| Concepto | Analogía |
| --- | --- |
| CI | Control de calidad en la fábrica antes de enviar el producto |
| Workflow | Receta automatizada del control de calidad |
| Trigger (`on:`) | “¿Cuándo arranca la inspección?” |
| Job / runner | Operario + mesa de trabajo en la nube |
| Step | Un paso de la receta |
| Badge verde | Sello de “última versión verificada” |
| `--cov-fail-under=60` | “Si la calidad baja del 60 %, no sale el lote” |

### 1.4 Regla de oro

> **Si CI está rojo, el código no está listo para entregar — da igual que “a ti te funcione”.**

---

# PARTE A — Tres conceptos clave (obligatorio)

> Prioridad: A1 → A2 → A3. El resto es profundidad.

---

## A1. Concepto clave 1 — Qué es CI y para qué sirve

### Definición operativa (DSIA)

**CI (Continuous Integration)** = cada vez que integras cambios en GitHub, una máquina limpia:

1. clona tu repo,
2. instala dependencias,
3. ejecuta la batería de validación (`pytest`, coverage, …),
4. marca el resultado: **éxito** o **fallo**.

### Por qué no basta con testear en local

| Solo local | Con CI |
| --- | --- |
| Depende de tu Python / venv | Misma versión en Ubuntu limpio |
| “Se me olvidó correr pytest” | Se corre en cada push/PR |
| El profesor no ve evidencia | Historial en Actions |
| “Funciona en mi cwd raro” | Se ve el fallo de rutas/paquetes |

### Checklist del concepto 1

- [ ] Sé explicar CI en una frase
- [ ] Sé decir qué dispara el workflow del curso (`push` a `main`, `pull_request`)
- [ ] Sé por qué CI usa una máquina limpia

---

## A2. Concepto clave 2 — Anatomía de un workflow (GitHub Actions)

Un workflow vive en:

```text
.github/workflows/ci.yml
```

### Piezas mínimas que debes reconocer

```yaml
name: proyecto-i-ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Tests + coverage
        run: |
          pytest -q --cov=ventas_app --cov=internet_app \
            --cov-report=term-missing --cov-fail-under=60
```

| Pieza | Pregunta que responde |
| --- | --- |
| `on:` | ¿Cuándo se ejecuta? |
| `jobs:` / `runs-on:` | ¿Dónde se ejecuta? |
| `steps:` | ¿Qué hace, en orden? |
| `uses: actions/checkout` | ¿Cómo obtiene el código? |
| `setup-python` | ¿Qué intérprete? |
| `pip install -r requirements.txt` | ¿Qué dependencias? |
| `pytest ... --cov-fail-under=60` | ¿Cuál es el gate de calidad? |

### Plantilla del curso

Copia y adapta: [`ejemplos/ci_proyecto_i.yml`](ejemplos/ci_proyecto_i.yml) → `.github/workflows/ci.yml` en **tu** repo.

### Checklist del concepto 2

- [ ] Sé localizar `.github/workflows/*.yml`
- [ ] Sé nombrar: trigger, job, step
- [ ] Sé adaptar `--cov=...` a mis paquetes reales

---

## A3. Concepto clave 3 — Gate verde en el Proyecto I

### Qué debe validar tu CI (mínimo DSIA)

1. Instalar desde `requirements.txt` (incluye `pytest`, `pytest-cov`, `pandas`, …).
2. Ejecutar tests del Proyecto I.
3. Exigir **cobertura ≥ 60 %** (`--cov-fail-under=60`).
4. Cambiar el workflow si algo de lo anterior falla.

### Evidencia de entrega

- Workflow presente en el repo.
- Al menos un run **verde** visible en la pestaña **Actions** (enlace o captura en el README).
- README con comandos locales **y** mención del workflow.

### Checklist del concepto 3

- [ ] Tengo `.github/workflows/ci.yml` en el repo del Proyecto I
- [ ] Actions muestra un run exitoso
- [ ] Si bajo cobertura a propósito, CI se pone rojo (entiendo el gate)

---

## A4. Mapa mental de los 3 conceptos

```text
CI (idea)           →  validar en cada integración
Workflow (YAML)     →  cómo se valida en GitHub
Gate Proyecto I     →  pytest + cov ≥ 60 % en verde
```

**Siguiente paso inmediato:** [`ejercicios/E4_ci_github.md`](ejercicios/E4_ci_github.md).

---

# PARTE B — Material suplementario

---

## B1. CI del repo de la asignatura (lectura guiada)

Abre [`.github/workflows/ci.yml`](../.github/workflows/ci.yml):

- Instala `requirements.txt` del curso.
- Corre pytest en `2_pruebas_y_despliegue/ejemplos`.
- Corre pytest en la plantilla E2E.

Tu Proyecto I es **otro repo**: no copies a ciegas los `working-directory` del curso; apunta a **tus** tests.

---

## B2. `requirements.txt` listo para CI

Ejemplo mínimo para Proyecto I:

```text
pandas>=2.2
pytest>=8.0
pytest-cov>=5.0
```

Sin `pytest-cov` en el remoto, el step de coverage fallará.

---

## B3. Unitarios vs integración en CI

Recomendación:

```bash
# En CI (gate principal): todo lo determinista
pytest -q --cov=... --cov-fail-under=60

# Opcional: separar
pytest -q -m "not integration"
pytest -q -m integration
```

Si un test de integración necesita ficheros, **inclúyelos en el repo** (muestra), no en tu Desktop.

---

## B4. Cómo depurar un Actions rojo

1. Abre el run fallido → el step en rojo.
2. Lee las últimas líneas del log (`AssertionError`, `No module named`, cov under 60, …).
3. Reproduce **el mismo comando** en local.
4. Empuja el fix; no “cerremos el PR igual”.

Fallos típicos:

| Síntoma | Causa habitual |
| --- | --- |
| `No module named ventas_app` | paquete mal nombrado / no hay `__init__.py` / cwd |
| cov &lt; 60 | faltan tests de cli/loader |
| fichero no encontrado | ruta absoluta o CSV no versionado |
| `pytest: command not found` | no instalaste requirements |

---

## B5. Badge en el README (opcional pero recomendable)

```markdown
![CI](https://github.com/<USER>/<REPO>/actions/workflows/ci.yml/badge.svg)
```

Sustituye `<USER>` y `<REPO>`.

---

## B6. Secretos y seguridad

- **Nunca** subas API keys al workflow ni al repo.
- Para Proyecto I no hace falta ningún secreto.
- Si más adelante usas claves: GitHub → Settings → Secrets and variables → Actions.

---

## B7. Anti-patrones frecuentes

1. Workflow que solo hace `echo ok`.
2. CI que no instala `pytest-cov` pero exige coverage.
3. Rutas `/Users/david/...` en tests o en YAML.
4. Ignorar Actions rojo y entregar igual.
5. Copiar el `ci.yml` del curso sin cambiar directorios/paquetes.
6. Tener tests solo en local y no en el repo.
7. Dependencias instaladas “a mano” en tu Mac y ausentes en `requirements.txt`.
8. Pedir `continue-on-error: true` para maquillar fallos.

---

## B8. Autoevaluación

### Clave

1. ¿Qué es CI en una frase?
2. ¿Dónde vive el workflow?
3. ¿Qué step falla si la cobertura es 45 %?
4. ¿Qué evidencia pides en el Proyecto I?

### Suplementario

5. ¿Cómo reproduces un fallo de Actions en local?
6. ¿Por qué CI usa Ubuntu y no tu portátil?

---

## B9. Checklist de salida

- [ ] Sé leer `on` / `jobs` / `steps`
- [ ] Plantilla copiada a mi repo y adaptada
- [ ] `requirements.txt` incluye `pytest` y `pytest-cov`
- [ ] Actions en verde con `--cov-fail-under=60`
- [ ] README documenta CI + enlace al run o badge

---

## B10. Para el Proyecto I / siguiente hito

1. Completa E4.  
2. No des por cerrado el 10 % sin CI verde.  
3. En Proyecto II reutilizarás el mismo esqueleto (añadiendo mocks/sklearn).

---

## B11. Apéndice A — Chuleta

```bash
# Local (igual que CI, en la medida de lo posible)
pytest -q
pytest -q --cov=ventas_app --cov=internet_app --cov-report=term-missing --cov-fail-under=60
```

```text
.github/workflows/ci.yml
requirements.txt
tests/
ventas_app/
internet_app/
```

---

## B12. Apéndice B — Glosario

| EN | ES / nota |
| --- | --- |
| continuous integration (CI) | integración continua |
| workflow | flujo / workflow de Actions |
| runner | máquina que ejecuta el job |
| artifact | artefacto (salidas guardadas; opcional) |
| badge | insignia de estado |
| gate | puerta de calidad (bloquea si falla) |

---

## B13. Apéndice C — Preguntas típicas

**¿Obligatorio GitHub Actions u otra CI?**  
En DSIA pedimos **GitHub Actions** (está en el flujo GitHub del curso).

**¿Puedo usar solo `pytest` en local sin CI?**  
No para dar por entregado el Proyecto I: CI es requisito.

**¿El coverage del curso tiene que ser 100 %?**  
No: el umbral del Proyecto I es **60 %**.

**¿Branches?**  
`push` a `main` + `pull_request` es el mínimo razonable.

---

## 14. Cierre

Si dominas la **Parte A**:

> **CI = validar el código en cada integración; el YAML describe cómo; el Proyecto I exige gate verde con pytest y cobertura ≥ 60 %.**

**Siguiente paso inmediato:** [`ejercicios/E4_ci_github.md`](ejercicios/E4_ci_github.md) + enunciado actualizado en `proyectos/proyecto_i/`.
