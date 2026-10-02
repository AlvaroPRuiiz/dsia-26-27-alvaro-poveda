# Proyecto III — Desarrollo End-to-End (40 %)

**Temas:** 1–5  
**Presentación del enunciado:** 19 de octubre de 2026  
**Release Candidate:** 23 de noviembre de 2026  
**Exposiciones:** 30 de noviembre de 2026

## Continuidad desde el Proyecto II

Este proyecto **amplía la base entregada en el Proyecto II** (mismo repo, mismo dominio, mismos datos, modelo sklearn y cliente de IA).

No se cambia de tema salvo causa justificada y acordada. El trabajo de octubre (pipeline, modelo, tests, mock/real) es el núcleo; aquí se completa el ciclo E2E.

## Objetivo

Diseñar, implementar, probar y desplegar una **solución completa** de datos e IA:

```text
Ingesta → Procesamiento → Modelo / IA → API → Dashboard web o de monitorización → Despliegue
```

Además de la API (o servicio backend), es **obligatorio** implementar una **interfaz web** o un **dashboard de monitorización** usable en la demo.

## Requisitos mínimos

1. Arquitectura modular y README claro (evolución del repo del Proyecto II).
2. Procesamiento de datos real (el dataset elegido en el II, salvo ampliación justificada).
3. Integración con el modelo sklearn y/o IA generativa (proveedor o mock justificado + interfaz lista para producción).
4. Pruebas automatizadas y evidencia de CI (GitHub Actions u otro).
5. **Dashboard de monitorización o aplicación web** que permita, como mínimo, una de estas líneas (o ambas):
   - **Producto:** explorar datos, lanzar predicciones / análisis y ver resultados.
   - **Operación:** ver salud del servicio (`/health`), métricas básicas, logs recientes o estado del pipeline/modelo.
   - Tecnologías admitidas: Dash, Streamlit, FastAPI+HTML/HTMX, Flask, o equivalente documentado.
6. Despliegue accesible **o** empaquetado listo con instrucciones verificables (API y dashboard).
7. Exposición de **5–7 minutos** + preguntas (incluye demo del dashboard/web).
8. Cumplimiento de la política de uso de IA (citas).

## Entrega

- Mismo repositorio del Proyecto II.
- README con: cómo entrenar/inferir, cómo arrancar API, cómo arrancar el dashboard/web, URL de despliegue si existe.
- Evidencia de que el dashboard consume el backend real (no solo capturas estáticas).

## Rúbrica orientativa

| Criterio | Peso |
| --- | --- |
| Complejidad y valor de la solución | 20 % |
| Calidad de código y arquitectura | 15 % |
| Integración datos + modelo/IA + API | 20 % |
| Dashboard web / monitorización | 15 % |
| Tests, robustez y despliegue | 15 % |
| Exposición y documentación | 15 % |

## Evaluación extraordinaria (referencia)

Si no se supera la ordinaria: aplicación completa (**70 %**) + examen (**30 %**), integrando los mismos bloques competenciales.
