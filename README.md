# Alfred - Assistente Pessoal

Assistente pessoal baseado em IA, single-tenant, guiado pela persona do mordomo Alfred. Recebe pedidos curtos via CLI, classifica a intencion, aplica politica de seguranca e responde em texto ou JSON.

## Estado do MVP

Este MVP implementa o nucleo racional do Alfred: entrada textual por CLI, roteamento de intencion (CHITCHAT, CLOUD_TASK, LOCAL_TASK, AMBIGUOUS, BLOCKED, OUT_OF_SCOPE), politica deterministica de seguranca, memoria efemera de sessao com TTL, tools simuladas sem efeitos colaterales e observabilidade segura (logs locais + LangSmith opcional).

## Instalacion

```bash
pip install -e .
```

Requiere Python >= 3.11.

## Configuracion de entorno

| Variable | Obligatoria | Descripcion |
|---|---|---|
| `OPENROUTER_API_KEY` | Si (router LLM) | Clave de OpenRouter para el clasificador LLM. |
| `ALFRED_ROUTER` | No | `llm` (por defecto) o `heuristic` para clasificacion offline deterministica sin LLM ni red. |
| `ALFRED_DATA_DIR` | No | Directorio de persistencia de sesiones (por defecto: dir de datos del usuario). |
| `ALFRED_LOG_LEVEL` | No | Nivel de log local (`INFO`, `WARNING`, `ERROR`). |
| `LANGSMITH_TRACING` | No | `true` habilita tracing en LangSmith (solo metadatos, sin contenido bruto). |
| `LANGSMITH_API_KEY` | No | Clave de LangSmith. |
| `LANGSMITH_PROJECT` | No | Proyecto LangSmith. |

## Uso de la CLI

```bash
alfred "mensaje"
alfred "mensaje" --session mi-sesion
alfred "mensaje" --json
alfred "mensaje" --no-trace
```

- **Texto** (por defecto): salida legible en terminal.
- **`--json`**: salida JSON parseable. En este modo la confirmacion interactiva queda deshabilitada (default-deny) para no contaminar stdout.
- **`--session`**: aísla el contexto efimero por `session_id` (TTL 2h).
- **`--no-trace`**: suprime eventos de telemetria.

Codigos de salida: `0` exito, `1` error de entrada, `2` error interno/configuracion.

### Modo offline (evaluacion y tests)

Sin `OPENROUTER_API_KEY` no hay llamadas LLM. Para validar el flujo completo en local:

```bash
export ALFRED_ROUTER=heuristic
export ALFRED_DATA_DIR=/tmp/alfred-data
alfred "check meu email inbox" --json --no-trace
```

El router heuristico clasifica por palabras clave y sirve como baseline de exactitud sobre el dataset de evaluacion.

## Tracing

- **Logs locales**: por defecto en stderr, con niveles por decision (INFO normal, WARNING para bloqueos/confirmaciones, ERROR para fallos de proveedor).
- **LangSmith**: solo cuando `LANGSMITH_TRACING=true` y `LANGSMITH_API_KEY` estan definidas. Nunca se registra el contenido bruto de mensajes ni respuestas; se envian metadatos, hashes, categoria, latencia y estado de seguridad.

## Tests y evaluacion de intencion

```bash
pytest                 # suite completa
pytest -m unit         # unitarios
pytest -m integration  # integracion
pytest -m e2e          # E2E de la CLI en proceso real
pytest --cov=src/alfred --cov-report=term-missing
```

Los tests E2E e de integracion ejecutan la CLI en un proceso real con entorno aislado (router heuristico, directorio temporal, sin red).

Dataset manual de intenciones: `tests/fixtures/eval_cases.py` (20 casos). El calculo de exactitud usa `alfred.eval.accuracy`:

```bash
python -c "from tests.fixtures.eval_cases import EVAL_CASES; from alfred.eval.accuracy import evaluate_dataset; print(evaluate_dataset([{'predicted_category': c['expected_category'], 'expected_category': c['expected_category']} for c in EVAL_CASES]))"
```

Objetivo del PRD: >= 85% de acierto en clasificacion.

## Limitaciones del MVP (fuera de alcance)

- **WhatsApp**: no se implementa servidor, webhook ni recepcion de mensajes en este MVP.
- **Servidor HTTP/API**: no existe endpoint publico.
- **Shell libre / automaciones reales**: no se ejecuta ningun comando libre ni automatizacion con efectos reales; las tools son simuladas.
- **Memoria permanente**: la sesion expira (TTL 2h) y no se persiste contenido bruto ni perfil del usuario.
- **Agentic loop / ejecucion proactiva**: sin iniciativa autonoma.
- **Multiusuario / permisos**: single-tenant.

## Estructura del Proyecto

```
src/alfred/
├── cli.py                # Adaptador CLI (entrada unica)
├── models.py             # Modelos Pydantic y enums
├── contracts.py          # Protocolos internos
├── config.py             # Configuracion
├── exceptions.py         # Excepciones customizadas
├── exit_codes.py         # Codigos de salida
├── app/                  # Capa de aplicacion (AssistantService + factory)
├── routing/              # Roteo de intenciones (LLM y heuristico)
├── safety/               # Politica de seguridad deterministica
├── memory/               # Memoria efimera de sesion (TTL)
├── llm/                  # Cliente OpenRouter/LangChain
├── tools/                # Tools simuladas sin efectos colaterales
├── eval/                 # Calculo de exactitud de intencion
└── observability/        # Logs locales + LangSmith opcional

tests/
├── unit/                 # Testes unitarios
├── integration/          # Testes de integracion y escenarios del PRD
├── e2e/                  # Testes E2E de la CLI en proceso real
└── fixtures/             # Fixtures y dataset de evaluacion
```

## Licencia

MIT