# E2E I — Arquitectura del flujo completo


## Exposición (30 min) — piezas

```text
[CSV / API origen]
        │
        ▼
   Ingesta + validación     (ingest.py / pipeline)
        │
        ▼
   Procesamiento / features
        │
        ▼
   Servicio de IA (API)     (ai_api_client / mock)
        │
        ▼
   API propia               (/health, /analyze)
        │
        ▼
   Logs + métricas
```

### Demo en vivo

```bash
cd 5_desarrollo_end_to_end/plantilla_proyecto
python ingest.py --input ../../3_automatizacion_e_ia/Datos/ventas.csv --output data/clean.csv
python app.py
```

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Texto de ejemplo suficientemente largo para el resumen mock del curso DSIA"}'
pytest -q
```

### Contratos que debes fijar el día 1 del Trabajo Final

1. Schema de entrada (columnas / JSON).
2. Schema de salida de `/analyze`.
3. Proveedor IA por defecto (`mock` en CI).
4. Criterio de “demo lista” (3 comandos).

Plantilla: `plantilla_proyecto/`. Enunciado: `proyectos/proyecto_iii/`.
