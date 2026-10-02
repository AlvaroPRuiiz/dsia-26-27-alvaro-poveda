# E2E II — Robustez, errores y logging


## Exposición (30 min)

### Taxonomía rápida

| Tipo | HTTP típico | Log |
| --- | --- | --- |
| Input inválido | 400 | WARNING |
| Dependencia caída | 502/503 | ERROR |
| Timeout | 504 | ERROR |
| Bug propio | 500 | ERROR + request_id |

### Logging útil

```python
import logging, time, uuid
logger = logging.getLogger("dsia.e2e")

request_id = str(uuid.uuid4())
t0 = time.perf_counter()
# ... llamada IA ...
logger.info(
    "analyze_ok request_id=%s latency_ms=%.1f provider=%s",
    request_id,
    (time.perf_counter() - t0) * 1000,
    "mock",
)
```

### Healthcheck

`/health` debe decir algo accionable (`degraded` si el path de datos no existe o el proveedor está en fallo).

### No hacer

- `except Exception: pass`
- Devolver stacktraces al cliente
- Loguear API keys o prompts con datos personales
