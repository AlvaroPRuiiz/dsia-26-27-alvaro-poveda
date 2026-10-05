# Sesión 19 oct 2026 — APIs de IA (OpenAI, Anthropic, Hugging Face)

| Recurso | Fichero |
| --- | --- |
| Demo (`ai_api_client`) | [`ejemplos/ai_api_client.py`](ejemplos/ai_api_client.py) |
| Ejercicio de clase | [`ejercicios/E5_apis_ia.md`](ejercicios/E5_apis_ia.md) |
| Variables de entorno (ejemplo) | [`.env.example`](../.env.example) |
| Base previa (data flows) | [`01_data_flows.md`](01_data_flows.md) |

Este documento es la **referencia amplia** de la sesión de APIs de IA: por qué unificar proveedores, los **tres conceptos clave** que debes dominar al salir de clase, y material suplementario (seguridad, errores, batch, citación, anti-patrones) para el Proyecto II y el resto del curso.

---

## 0. Objetivos de aprendizaje

### Obligatorios (los 3 conceptos clave)

Al terminar la sesión **debes** ser capaz de:

1. Usar un **cliente unificado** (`complete`) que normaliza la respuesta en `AIResponse` independientemente del proveedor.
2. Gestionar **secretos** con `.env` / `.env.example` y desarrollar/CI en modo **`mock`** (sin claves ni red).
3. Aplicar una política de **errores y reintentos**: qué reintentar, qué no, y cuándo fallar explícito.

### Deseables (material suplementario)

4. Lanzar el demo con `openai` / `anthropic` / `hf` si hay claves (opcional en aula).
5. Extender el CLI con batch JSONL + retries (E5).
6. Documentar uso de IA en `AI_USAGE.md`.
7. Encajar el cliente como **borde** del pipeline (no dentro de `transform`).

---

## 1. Por qué esta sesión importa en DSIA

### 1.1 Qué entregamos

En DSIA no entregamos “un notebook que llama a ChatGPT con la clave pegada”. Entregamos un **borde de aplicación** que:

1. elige proveedor por configuración,
2. lee secretos del entorno,
3. normaliza la respuesta,
4. falla de forma controlada,
5. se puede ejercitar en CI con **mock**.

Sin eso, cada cambio de proveedor o de clave rompe el pipeline y los tests.

### 1.2 Mapa mental del semestre

```text
Tema 1  →  pandas + arquitectura (etapas y módulos)
Tema 2  →  pytest + CI (confianza)
Tema 3  →  data flows + APIs IA (hoy)   ← automatizas el núcleo y el borde IA
Tema 4  →  asistentes / refactor con IA
Tema 5  →  E2E / deploy
```

El data flow de la sesión anterior es el **centro**. La API de IA es otro **borde** (como `load`/`save`): Strategy + mock, no lógica de negocio mezclada.

### 1.3 Analogías útiles

| Concepto | Analogía |
| --- | --- |
| Cliente unificado | Mandos universales: mismo botón, distintas TVs |
| `AIResponse` | Ticket estándar de respuesta (da igual el mostrador) |
| Proveedor (`openai` / …) | El mostrador concreto |
| Modo `mock` | Simulador de vuelo: practicas sin avión real |
| `.env` | Caja fuerte; el código solo pide la llave |
| Retry / backoff | Llamar otra vez si la línea está saturada |
| 401/403 | Llave incorrecta: no sirve llamar 10 veces |
| `AI_USAGE.md` | Recibo de qué IA usaste y qué aceptaste |

### 1.4 Regla de oro

> **Secretos fuera del código; mock en CI; respuesta normalizada; reintenta solo lo transitorio.**

---

# PARTE A — Tres conceptos clave (obligatorio)

> Prioridad de clase: domina A1 → A2 → A3. El resto del documento es red de seguridad y profundidad.

---

## A1. Concepto clave 1 — Cliente unificado + `AIResponse`

### Qué es

Un **cliente unificado** es una función (o clase) que:

1. recibe `provider` + `prompt` (+ `model` opcional),
2. habla con el SDK correspondiente,
3. devuelve siempre la misma forma: `AIResponse(provider, text)`.

```text
Tu aplicación ──► complete(provider, prompt) ──► Proveedor (mock|openai|anthropic|hf)
                      │
                      └─► AIResponse(provider, text)
```

En el demo:

```python
@dataclass
class AIResponse:
    provider: str
    text: str


def complete(provider: str, prompt: str, model: str | None = None) -> AIResponse:
    ...
```

### Demo mínima

```bash
cd 3_automatizacion_e_ia/ejemplos
python ai_api_client.py --provider mock --prompt "Resume Clean Code en 3 bullets"
```

Salida esperada: prefijo `[mock]` y un eco del prompt (sin red, sin claves).

### Por qué importa en DSIA

Tu pipeline / Proyecto II debe poder cambiar de proveedor **sin** reescribir `transform` ni los tests. El borde IA cambia; el contrato `AIResponse` se mantiene.

### Checklist del concepto 1

- [ ] Sé lanzar el demo en modo `mock`
- [ ] Sé explicar qué campos tiene `AIResponse`
- [ ] Sé decir por qué no llamamos al SDK desde dentro de `transform`

---

## A2. Concepto clave 2 — Secretos + modo `mock`

### 2.1 Secretos en el entorno

Las claves **no** van en el código ni en GitHub.

```bash
# Desde la raíz del repo del curso
cp .env.example .env
# Edita .env con tus claves (si las tienes). No lo subas.
```

| Variable | Uso |
| --- | --- |
| `OPENAI_API_KEY` | proveedor `openai` |
| `ANTHROPIC_API_KEY` | proveedor `anthropic` |
| `HF_TOKEN` | proveedor `hf` |
| `LOG_LEVEL` | logging (opcional) |

El demo usa `python-dotenv` + `os.getenv(...)`. Si falta la clave → `AIClientError` claro.

### 2.2 Modo `mock` obligatorio

```python
if provider == "mock":
    return AIResponse(provider="mock", text=f"[mock] Recibido: {prompt[:200]}")
```

Úsalo para:

- desarrollo offline,
- CI / Actions (sin secretos de IA en el Proyecto I/II básico),
- demos en aula sin depender de cuota/red.

### Checklist de seguridad (mínimo)

1. Claves solo en `.env` / secretos del PaaS / GitHub Secrets.  
2. `.env` en `.gitignore`; existe `.env.example` sin valores reales.  
3. No loguear prompts con PII.  
4. Modo `mock` en CI y en el camino feliz de desarrollo.

### Por qué importa en DSIA

Una clave filtrada en un commit es un incidente. Un test que llama a OpenAI en cada push es lento, caro y flaky. Mock + env resuelve ambos.

### Checklist del concepto 2

- [ ] Sé copiar `.env.example` → `.env` y explicar por qué `.env` no se versiona
- [ ] Sé correr el cliente sin ninguna clave (`--provider mock`)
- [ ] Sé listar las 4 reglas de seguridad de arriba

---

## A3. Concepto clave 3 — Errores, timeouts y reintentos

### Qué es

No todos los fallos se tratan igual:

| Situación | Estrategia |
| --- | --- |
| 401 / 403 | Configuración (clave/permisos); **no** reintentar a ciegas |
| 429 | Backoff + jitter (la API te pide esperar) |
| 5xx / timeout | Reintento **limitado** + fallback / error tipado |
| Respuesta vacía | Validar y fallar explícito (`AIClientError`) |
| Proveedor desconocido / falta SDK | Fallar claro; no silenciar |

En el demo base, los fallos de configuración ya son `AIClientError`. En el **E5** añades reintentos simulados con `--fail-once`.

### Idea de retry (E5)

```text
intento 1 → fallo transitorio
sleep corto
intento 2 → OK  (o agotar reintentos y propagar AIClientError)
```

Regla práctica:

> **Reintenta lo transitorio; no reintentes lo de configuración.**

### Por qué importa en DSIA

Una API real falla. Si tu job aborta a la primera 503 sin criterio, el pipeline es frágil. Si reintentas un 401 en bucle, quemas tiempo y no arreglas nada.

### Checklist del concepto 3

- [ ] Sé clasificar 401 vs 429 vs 5xx en una frase cada uno
- [ ] Sé explicar por qué el mock permite practicar retries sin gastar cuota
- [ ] Sé qué pedirá E5 (`--fail-once` + hasta 2 reintentos)

---

## A4. Mapa mental de los 3 conceptos

```text
Cliente unificado + AIResponse  →  mismo contrato, varios proveedores
Secretos + mock                 →  seguro offline y en CI
Errores / retries               →  fallar bien; reintentar solo lo transitorio
```

Si dominas eso, puedes hacer el E5 y enchufar IA al Proyecto II sin ensuciar el núcleo.

**Siguiente paso inmediato en clase:** [`ejercicios/E5_apis_ia.md`](ejercicios/E5_apis_ia.md).

---

# PARTE B — Material suplementario

> Úsalo para profundizar, preparar el E5/Proyecto II y resolver dudas. **No** sustituye a A1–A3.

---

## B1. Anatomía del demo `ai_api_client.py`

| Pieza | Rol |
| --- | --- |
| `AIResponse` | Contrato de salida normalizado |
| `AIClientError` | Error tipado del borde IA |
| `complete(...)` | Strategy por `provider` |
| `load_dotenv()` | Carga `.env` al arrancar |
| `main` / `argparse` | CLI: `--provider`, `--prompt`, `--model` |

Proveedores soportados en el demo:

| `--provider` | SDK / nota | Variable |
| --- | --- | --- |
| `mock` | sin red | ninguna |
| `openai` | `openai.OpenAI` | `OPENAI_API_KEY` |
| `anthropic` | `anthropic.Anthropic` | `ANTHROPIC_API_KEY` |
| `hf` | `huggingface_hub.InferenceClient` | `HF_TOKEN` |

---

## B2. Guion de exposición (30 min)

1. Mensaje: notebook con clave pegada ≠ borde de producto (5 min).  
2. Dibujar el mapa A1 + lanzar demo `mock` (8 min).  
3. Abrir `.env.example` y checklist de seguridad A2 (7 min).  
4. Tabla de errores A3 + adelanto E5 (batch + `--fail-once`) (10 min).

---

## B3. Demo con claves reales (opcional en aula)

Solo si hay cuota y el profesor lo indica:

```bash
cp ../.env.example ../.env   # desde ejemplos/ o desde la raíz del repo
# Rellena OPENAI_API_KEY / ANTHROPIC_API_KEY / HF_TOKEN

cd 3_automatizacion_e_ia/ejemplos
python ai_api_client.py --provider openai --prompt "Resume SOLID en 3 viñetas"
python ai_api_client.py --provider anthropic --prompt "..."
python ai_api_client.py --provider hf --prompt "..."
```

Si falta la clave o el SDK:

```text
AIClientError: Falta OPENAI_API_KEY en el entorno
AIClientError: Instala el SDK: pip install openai
```

Eso es **deseable**: fallar explícito > traza opaca.

---

## B4. Batch JSONL y retries (puente al E5)

El ejercicio de clase pide extender el demo:

1. `--batch prompts.txt` + `--output respuestas.jsonl` (5 prompts → 5 líneas JSON).  
2. `--fail-once` + hasta 2 reintentos con `sleep` corto.  
3. `AI_USAGE.md` con proveedor + citación.

Formato mínimo de cada línea JSONL:

```json
{"prompt": "...", "provider": "mock", "text": "..."}
```

No hace falta proveedor real para completar E5.

---

## B5. `AI_USAGE.md` (citación)

En DSIA documentamos el uso de asistentes/APIs:

```text
# AI usage

- Provider: mock
- Asistente: <ninguno | Cursor / ChatGPT / …>
- Qué aportó: …
- Qué acepté / revisé: …
- Comandos de evidencia: …
```

Objetivo: trazabilidad académica y hábito profesional (qué generó la máquina vs qué validaste tú).

---

## B6. Encaje con el data flow / Proyecto II

```text
load → validate/transform → (sklearn) → borde IA (complete) → save / metrics
         ↑ puro, testeable              ↑ mock en tests/CI
```

Reglas:

- No pegues la llamada OpenAI dentro de `transform`.  
- Tests del cliente IA: **mock** (o stub de `complete`).  
- CI del Proyecto II no debe depender de claves de pago.

---

## B7. Anti-patrones frecuentes (lista negra)

1. API key hardcodeada en `.py` o en el README.  
2. Subir `.env` a GitHub.  
3. Llamar al proveedor real en cada test de CI.  
4. Mezclar descarga HTTP + prompt LLM + pandas en la misma función.  
5. `except: pass` alrededor de la llamada a la API.  
6. Reintentar 401/403 en bucle.  
7. Loguear el prompt completo con datos personales.  
8. Acoplar el resto de la app a tipos del SDK (`ChatCompletion`) en vez de `AIResponse`.  
9. Un solo `if provider == "openai"` repartido por todo el repo (sin cliente unificado).  
10. Celebrar “funciona en mi Mac con la clave en el shell” sin `.env.example`.

---

## B8. Autoevaluación (clave vs suplementario)

### Clave (debe salir fluido)

1. ¿Qué es un cliente unificado y qué devuelve?  
2. ¿Por qué existe el modo `mock`?  
3. ¿Dónde viven las claves y qué fichero de ejemplo versionamos?  
4. ¿Qué errores se reintentan y cuáles no?

### Suplementario

5. ¿Por qué la IA no va dentro de `transform`?  
6. ¿Qué pides en cada línea del JSONL del E5?  
7. ¿Para qué sirve `AI_USAGE.md`?

Si fallas en 1–4, rehaz la Parte A y el demo `mock` antes del E5.

---

## B9. Checklist de salida

### Conceptos clave

- [ ] Demo `mock` lanzado por ti  
- [ ] Sé explicar `AIResponse` + `complete`  
- [ ] Sé aplicar el checklist de secretos / mock  
- [ ] Sé clasificar 401 / 429 / 5xx  

### Ejercicio / proyecto

- [ ] E5: batch JSONL con 5 registros  
- [ ] E5: retry con `--fail-once`  
- [ ] `AI_USAGE.md` escrito  
- [ ] Idea clara de cómo enchufar el borde IA al Proyecto II  

---

## B10. Para la siguiente sesión / hito

1. Completa E5 en modo `mock`.  
2. No metas claves en el repo del Proyecto II.  
3. Cuando uses asistentes en Tema 4, el mismo criterio de citación (`AI_USAGE.md`) se mantiene.

---

## B11. Apéndice A — Chuleta rápida

```bash
cd 3_automatizacion_e_ia/ejemplos
python ai_api_client.py --provider mock --prompt "Di hola en una frase"

# Tras E5:
python ai_api_client.py --provider mock --batch prompts.txt --output respuestas.jsonl
python ai_api_client.py --provider mock --prompt "test" --fail-once
```

```python
from ai_api_client import complete, AIResponse, AIClientError

resp: AIResponse = complete("mock", "Hola")
assert resp.provider == "mock"
assert resp.text.startswith("[mock]")
```

---

## B12. Apéndice B — Glosario corto EN/ES

| EN | ES / nota |
| --- | --- |
| provider | proveedor (OpenAI, Anthropic, HF, mock) |
| API key / token | clave / token de acceso |
| retry / backoff | reintento / espera creciente |
| jitter | aleatoriedad en la espera (evita thundering herd) |
| rate limit (429) | límite de tasa |
| mock | simulacro / doble de prueba |
| secrets | secretos (credenciales) |
| JSONL | JSON Lines (un JSON por línea) |

---

## B13. Apéndice C — Preguntas típicas de clase

**¿Obligatorio pagar OpenAI?**  
No para la sesión ni el E5: el modo `mock` basta. Las claves reales son opcionales.

**¿Puedo usar solo un proveedor en el Proyecto II?**  
Sí, pero deja el **cliente unificado** + mock para tests/CI.

**¿Dónde pongo la clave en GitHub Actions?**  
Settings → Secrets. Para el gate básico del curso, **mock** evita el secreto.

**¿Qué modelo uso?**  
Los defaults del demo (`gpt-4o-mini`, Claude Sonnet, Mistral en HF) son punto de partida; puedes pasar `--model`.

**¿Por qué `AIClientError` y no `Exception` genérica?**  
Para que los tests y el CLI puedan distinguir fallos del borde IA.

**¿El batch JSONL es obligatorio en el Proyecto II?**  
Es el ejercicio de clase (E5). En el proyecto, reutiliza la idea (contratos claros + evidencia) aunque el formato exacto cambie.

---

## B14. Apéndice D — Mini rúbrica de autocontrol (APIs IA)

| Criterio | Insuficiente | Adecuado | Sólido |
| --- | --- | --- | --- |
| Cliente | SDK pegado en el notebook | `complete` + `AIResponse` | + fácil añadir proveedor |
| Secretos | Clave en código | `.env` + `.env.example` | + mock en CI |
| Errores | Silenciados / siempre retry | Tabla 401/429/5xx aplicada | + retries acotados (E5) |
| Proyecto II | IA dentro de `transform` | Borde separado | + tests mock + `AI_USAGE.md` |

---

## 14. Cierre

Si dominas la **Parte A**, tienes lo esencial de la sesión:

> **Cliente unificado + secretos/mock + errores con criterio = borde de IA listo para producto y para CI.**

El material suplementario (batch, citación, anti-patrones) te prepara para el E5 y para enchufar IA al Proyecto II sin romper el pipeline.

**Siguiente paso inmediato:** haz [`ejercicios/E5_apis_ia.md`](ejercicios/E5_apis_ia.md) y conecta los 3 conceptos al demo `ai_api_client.py`.
