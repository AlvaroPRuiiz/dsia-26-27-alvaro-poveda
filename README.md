# Desarrollo de Soluciones de IA (Curso 2026-2027)

## Información general

Asignatura de máster orientada al **diseño, implementación y despliegue de soluciones de datos e inteligencia artificial** con Python. Las sesiones son **semanales de 1 h 45 min**.

Al finalizar, el alumnado será capaz de:

1. Escribir código Python robusto, modular y testeable.
2. Automatizar flujos de datos e integrar servicios de IA vía APIs.
3. Usar IA generativa como herramienta de desarrollo de forma responsable.
4. Entregar una solución end-to-end desplegable (datos → modelo/API → monitorización).

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| `1_programacion_avanzada_python/` | Tema 1 — estructuras, OOP, errores, pandas, Clean Code |
| `2_pruebas_y_despliegue/` | Tema 2 — pytest, Git, entornos, CI/CD |
| `3_automatizacion_e_ia/` | Tema 3 — data flows, APIs, servicios de IA |
| `4_entornos_ia_generativa/` | Tema 4 — asistentes, prompts, documentación y tests con IA |
| `5_desarrollo_end_to_end/` | Tema 5 — arquitectura E2E, despliegue y monitorización |
| `proyectos/` | Enunciados de Proyecto I, II y III |

## Temario

### Tema 1: Programación avanzada en Python
- Estructuras de datos avanzadas
- Programación orientada a objetos
- Tratamiento de errores y excepciones
- Manipulación y validación de datos
- Buenas prácticas, organización y documentación del código

### Tema 2: Pruebas y despliegue
- Pruebas unitarias e integración
- Control de versiones con Git
- Gestión de dependencias y entornos virtuales
- Entornos de desarrollo y producción
- Automatización de pruebas e introducción a CI/CD

### Tema 3: Automatización de tareas e IA
- Automatización de procesos con Python
- Construcción de flujos de datos
- Integración y consumo de APIs
- Integración de servicios de IA
- Automatización con IA generativa
- Gestión de errores y monitorización

### Tema 4: Entornos de desarrollo con IA generativa
- IA generativa aplicada al desarrollo
- Asistentes de programación (Claude Code, Gemini CLI, Cursor, …)
- Generación y mejora de código
- Diseño de prompts para programación
- Generación de documentación y pruebas
- Buenas prácticas y citación del uso de IA

### Tema 5: Desarrollo End-to-End
- Diseño de soluciones de datos e IA
- Preparación y procesamiento de datos
- Desarrollo e integración de modelos / APIs
- Pruebas, validación, despliegue, monitorización y mantenimiento

## Formato de clase

En las sesiones lectivas: **30 min exposición + 30 min ejercicios** + ~45 min de proyecto/presentaciones. El material público está en las carpetas de cada tema (`1_…` … `5_…`) y en `proyectos/`.

## Calendario de sesiones (2026)

| Fecha | Contenido | Material público |
| --- | --- | --- |
| **7 sep** | Presentación + entornos virtuales Python + Git/GitHub | `1_programacion_avanzada_python/01_entornos_y_git.md` |
| **14 sep** | Pandas + ejercicios + presentación Proyecto I | `1_programacion_avanzada_python/02_pandas_datos.ipynb` |
| **21 sep** | Arquitectura, Clean Code y SOLID + ejercicios | `1_programacion_avanzada_python/03_arquitectura_patrones.md` |
| **28 sep** | pytest + CI (GitHub Actions) + ejercicios | `2_pruebas_y_despliegue/` |
| **5 oct** | Data flows + proyecto | `3_automatizacion_e_ia/` |
| **19 oct** | APIs de IA + presentación Trabajo Final | `3_automatizacion_e_ia/` · `proyectos/proyecto_iii/` |
| **26 oct** | E2E I: arquitectura del flujo | `5_desarrollo_end_to_end/` |
| **16 nov** | E2E II: robustez, logging y despliegue | `5_desarrollo_end_to_end/` |
| **23 nov** | Claude Code / Gemini CLI / Cursor + Release Candidate | `4_entornos_ia_generativa/` |
| **30 nov** | Presentación Trabajo Final | — |

## Evaluación ordinaria

| Elemento | Peso | Temas |
| --- | --- | --- |
| **Proyecto I** — Programación avanzada en Python (ventas + dataset de internet) | **10 %** | Tema 1 |
| **Proyecto II** — Automatización e integración de servicios | **20 %** | Temas 2, 3 y 4 |
| **Proyecto III** — Desarrollo End-to-End | **40 %** | Temas 1–5 |
| **Examen final** teórico-práctico | **30 %** | Temas 1–5 |

Detalle de enunciados en `proyectos/`.

## Evaluación extraordinaria

| Elemento | Peso |
| --- | --- |
| Desarrollo de una aplicación / cuadro de mando completo | **70 %** |
| Examen teórico-práctico | **30 %** |

## Uso de herramientas de Inteligencia Artificial

El uso de IA para elaborar trabajos (completos o partes relevantes) debe seguir las indicaciones de cada actividad. Cuando esté permitido, **hay que indicar y citar** la herramienta utilizada. El uso no autorizado, o sin referencia, se considerará **plagio** según el Reglamento General de la Universidad.

## Entorno de trabajo

```bash
git clone git@github.com:dmartincc/dsia-26-27.git
cd dsia-26-27
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Recursos
- [Python docs](https://docs.python.org/3/)
- [pytest](https://docs.pytest.org/)
- [pandas](https://pandas.pydata.org/docs/)
- [Hugging Face](https://huggingface.co/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
