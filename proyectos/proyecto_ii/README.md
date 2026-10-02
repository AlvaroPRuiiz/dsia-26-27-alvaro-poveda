# Proyecto II — Automatización e integración de servicios (20 %)

**Temas:** 2, 3 y 4  
**Trabajo continuo:** octubre 2026  
**Hito de presentación del Trabajo Final (enunciado E2E):** 19 de octubre de 2026

## Relación con el Proyecto III

El Proyecto II **es la base del Proyecto III (Trabajo Final)**.

- Eliges **ya** el dominio, los datos y el problema que llevarás al E2E.
- El repo, el pipeline, el modelo sklearn, los tests y el cliente de IA de esta entrega **se reutilizan y se amplían** en el Proyecto III (API/app, despliegue, monitorización, RC y exposición).
- No se parte de cero en noviembre: el III continúa este mismo trabajo.

```text
Proyecto II (base)                         Proyecto III (ampliación)
─────────────────                          ────────────────────────
datos + pipeline + logs               →    + API / app
modelo sklearn entrenado + inferencia →    + endpoint de predicción (o integrado)
cliente IA generativa (mock + real)   →    + contrato /analyze (o equivalente)
pytest + .env.example                 →    + CI + robustez
README / AI_USAGE                     →    + despliegue + monitorización + exposición
```

## Objetivo

Automatizar un proceso de datos que combine:

1. un **modelo clásico de scikit-learn** entrenado e integrado en el pipeline, y  
2. al menos un **servicio de IA generativa vía API**,

con pruebas y buenas prácticas de entornos, **dejando el código listo para crecer hacia el E2E**.

## Requisitos mínimos

1. **Elección de dominio y datos para tu Proyecto III** (documentada en el README: origen, licencia, motivación).
2. Pipeline reproducible (CLI o job) con logs.
3. **Entrenamiento de un modelo scikit-learn** (clasificación, regresión o similar) adecuado al dataset:
   - script o módulo de entrenamiento reproducible (`train` / equivalente);
   - persistencia del modelo (`joblib` / `pickle` u otro formato documentado);
   - **inferencia integrada en el pipeline** (no solo un notebook suelto);
   - métricas de evaluación básicas reportadas en README o informe generado (p. ej. accuracy, F1, RMSE…).
4. Tests pytest (unitarios + al menos un test de integración o marcado), incluyendo al menos un test que cubra la **carga/inferencia del modelo** (puede usar un fixture o modelo pequeño).
5. Cliente de IA generativa con modo `mock` y un proveedor real documentado (si no hay clave, mock + diseño listo).
6. `.env.example` y `requirements.txt` (incluye `scikit-learn`).
7. Sección `AI_USAGE.md` citando herramientas de IA usadas en el desarrollo.
8. Estructura modular que permita añadir después API y despliegue **sin reescribir** el núcleo.

## Entrega

- Repo GitHub **del Trabajo Final** (el mismo que usarás en el Proyecto III).
- Historial de commits a lo largo de octubre.
- Artefactos del modelo versionados con criterio (modelo entrenado y/o instrucciones claras para reentrenar).
- README que deje claro: datos → entrenamiento sklearn → pipeline con inferencia → IA generativa, y **qué se ampliará** en el III.

## Rúbrica orientativa

| Criterio | Peso |
| --- | --- |
| Pipeline y automatización | 20 % |
| Modelo sklearn (entrenamiento + integración) | 20 % |
| Integración API / IA generativa | 20 % |
| Tests y calidad | 15 % |
| Robustez (errores, logs, config) | 10 % |
| Documentación, citación IA y continuidad hacia el III | 15 % |
