# Sesión 19 oct 2026 — APIs de IA (OpenAI, Anthropic, Hugging Face)

Ejercicio 30 min: `ejercicios/E5_apis_ia.md`  
Demo: `ejemplos/ai_api_client.py`

## Exposición (30 min) — mapa mental

```text
Tu aplicación ──► Cliente unificado ──► Proveedor (mock|openai|anthropic|hf)
                      │
                      ├─ timeouts / retries
                      ├─ secretos vía env
                      └─ respuesta normalizada (AIResponse)
```

### Checklist de seguridad

1. Claves solo en `.env` / secretos del PaaS.
2. `.env` en `.gitignore`; existe `.env.example`.
3. No loguear prompts con PII.
4. Modo `mock` obligatorio para CI y desarrollo offline.

### Demo

```bash
cp ../.env.example ../.env   # desde la raíz del repo
cd 3_automatizacion_e_ia/ejemplos
python ai_api_client.py --provider mock --prompt "Resume Clean Code en 3 bullets"
```

Con claves reales (opcional en aula):

```bash
python ai_api_client.py --provider openai --prompt "..."
python ai_api_client.py --provider anthropic --prompt "..."
python ai_api_client.py --provider hf --prompt "..."
```

### Errores que debes enseñar a manejar

| Situación | Estrategia |
| --- | --- |
| 401/403 | Configuración; no reintentar a ciegas |
| 429 | Backoff + jitter |
| 5xx / timeout | Reintento limitado + fallback |
| Respuesta vacía | Validar y fallar explícito |

## Ejercicios

`E5_apis_ia.md`: batch JSONL + retries + `AI_USAGE.md`.
