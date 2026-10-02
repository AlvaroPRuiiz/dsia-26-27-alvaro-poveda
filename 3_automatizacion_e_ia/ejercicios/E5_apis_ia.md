# E5 — Cliente multi-API de IA (30 min)

**Sesión:** 19 oct 2026  
**Base:** `../ejemplos/ai_api_client.py`

## Parte 1 — Smoke mock (5 min)

```bash
python ai_api_client.py --provider mock --prompt "Di hola en una frase"
```

## Parte 2 — Batch JSONL (10 min)

1. Crea `prompts.txt` con 5 líneas.
2. Añade `--batch prompts.txt --output respuestas.jsonl`.
3. Cada línea del JSONL: `{"prompt": "...", "provider": "mock", "text": "..."}`.

## Parte 3 — Reintentos (8 min)

Simula un fallo (función interna o flag `--fail-once`) y reintenta hasta 2 veces con sleep corto antes de propagar `AIClientError`.

## Parte 4 — Citación (7 min)

Crea/actualiza `AI_USAGE.md`:

- Proveedor usado en la práctica (mock o real)
- Si un asistente escribió parte del código: herramienta + qué aceptaste

## Hecho cuando…

`respuestas.jsonl` tiene 5 registros y el README/AI_USAGE documenta el uso.
