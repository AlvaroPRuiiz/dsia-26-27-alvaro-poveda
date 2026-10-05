# E5 — Cliente multi-API de IA (30 min)

**Sesión:** 19 oct 2026  
**Referencias:** [`../02_apis_ia.md`](../02_apis_ia.md) · base [`../ejemplos/ai_api_client.py`](../ejemplos/ai_api_client.py)

## Meta

Extender el cliente unificado para que soporte **batch JSONL**, **reintentos** ante fallos transitorios y documente el uso de IA en `AI_USAGE.md`. Trabaja en modo `mock` (sin claves).

## Parte 0 — Smoke mock (5 min)

```bash
cd 3_automatizacion_e_ia/ejemplos
python ai_api_client.py --provider mock --prompt "Di hola en una frase"
```

Confirma que imprime algo como `[mock]` + el texto eco. Si falla el import de `dotenv`, instala `python-dotenv` en tu entorno del curso.

## Parte 1 — Batch JSONL (10 min)

1. Crea `prompts.txt` con **5 líneas** (un prompt por línea).
2. Extiende el CLI con:
   - `--batch PATH` — lee prompts línea a línea
   - `--output PATH` — escribe JSONL (una respuesta por línea)
3. Cada línea del JSONL debe tener al menos:

```json
{"prompt": "...", "provider": "mock", "text": "..."}
```

Ejemplo de uso:

```bash
python ai_api_client.py --provider mock --batch prompts.txt --output respuestas.jsonl
```

> Si pasas `--batch`, `--prompt` deja de ser obligatorio.

## Parte 2 — Reintentos (8 min)

1. Añade un flag `--fail-once` (o equivalente interno) que haga fallar la **primera** llamada a `complete` con `AIClientError`.
2. Envuelve la llamada con hasta **2 reintentos** y un `sleep` corto (p. ej. 0.2 s) entre intentos.
3. Si agotas los reintentos → propaga `AIClientError`.

Prueba manual:

```bash
python ai_api_client.py --provider mock --prompt "test" --fail-once
# debe recuperar tras el primer fallo y devolver texto mock
```

## Parte 3 — Citación (7 min)

Crea o actualiza `AI_USAGE.md` (en el ejemplo o en tu repo de práctica) con:

- Proveedor usado en la práctica (`mock` y, si aplica, uno real)
- Si un asistente escribió parte del código: herramienta + qué aceptaste / qué cambiaste
- Comando(s) que demuestran el batch y el retry

Plantilla mínima:

```text
# AI usage

- Provider: mock
- Asistente: <ninguno | Cursor / ChatGPT / …>
- Qué aportó: …
- Qué acepté / revisé: …
- Comandos:
  python ai_api_client.py --provider mock --batch prompts.txt --output respuestas.jsonl
  python ai_api_client.py --provider mock --prompt "test" --fail-once
```

## Hecho cuando…

- [ ] `respuestas.jsonl` tiene **5** registros válidos
- [ ] El retry con `--fail-once` recupera y no deja caer el proceso a la primera
- [ ] Existe `AI_USAGE.md` con proveedor + citación
- [ ] Entiendes por qué el modo `mock` es obligatorio en CI / desarrollo offline
