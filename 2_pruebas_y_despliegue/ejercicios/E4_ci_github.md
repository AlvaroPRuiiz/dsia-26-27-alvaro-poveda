# E4 — CI con GitHub Actions para el Proyecto I (30 min)

**Sesión:** 28 sep 2026  
**Referencias:** [`../02_ci_github.md`](../02_ci_github.md) · plantilla [`../ejemplos/ci_proyecto_i.yml`](../ejemplos/ci_proyecto_i.yml)

## Meta

Dejar tu repo del Proyecto I con un workflow que **valide el código** en cada push/PR: `pytest` + **cobertura ≥ 60 %**.

## Parte 0 — Lectura rápida (5 min)

1. Abre el CI del curso: `../../.github/workflows/ci.yml`.
2. Abre la plantilla: `../ejemplos/ci_proyecto_i.yml`.
3. Escribe en una frase: *qué* valida y *cuándo* se ejecuta.

## Parte 1 — Preparar el repo (8 min)

En **tu** repo del Proyecto I:

1. Asegura `requirements.txt` con al menos:

```text
pandas>=2.2
pytest>=8.0
pytest-cov>=5.0
```

2. Verifica en local:

```bash
pytest -q
pytest -q --cov=ventas_app --cov=internet_app --cov-report=term-missing --cov-fail-under=60
```

> Adapta `--cov=...` a tus paquetes. Si falla el 60 %, añade tests (cli/loader/…) antes de seguir.

## Parte 2 — Workflow (10 min)

1. Crea `.github/workflows/ci.yml` copiando la plantilla.
2. Ajusta paquetes / rutas si hace falta.
3. Commit + push a GitHub.

```bash
git add .github/workflows/ci.yml requirements.txt
git commit -m "Add GitHub Actions CI with pytest coverage gate"
git push
```

## Parte 3 — Evidencia (5 min)

1. Abre la pestaña **Actions** de tu repo.
2. Confirma un run **verde**.
3. Añade al README:

```markdown
## CI

Workflow: `.github/workflows/ci.yml`

```bash
pytest -q --cov=ventas_app --cov=internet_app --cov-report=term-missing --cov-fail-under=60
```

Enlace al último run verde: <URL>
```

(Opcional) badge:

```markdown
![CI](https://github.com/<USER>/<REPO>/actions/workflows/ci.yml/badge.svg)
```

## Parte 4 — Comprobar el gate (2 min)

Elige **una**:

- Baja temporalmente `--cov-fail-under` a `95` **en una rama** y observa el rojo, luego revertir; o
- Comenta un test crítico, empuja, mira el fallo, restaura.

Objetivo: ver que CI **bloquea** calidad insuficiente.

## Hecho cuando…

- [ ] Existe `.github/workflows/ci.yml`
- [ ] Actions en verde con coverage gate 60 %
- [ ] README documenta el comando y el enlace/badge
- [ ] Entiendes por qué el Proyecto I exige CI (no solo pytest local)
