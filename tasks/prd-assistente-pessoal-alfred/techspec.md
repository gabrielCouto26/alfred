# Especificação Técnica

## Resumo Executivo

O MVP do Alfred será um assistente pessoal local executado via CLI, implementado em Python, com LangChain como harness de orquestração, OpenRouter como provedor LLM prioritário e LangSmith para tracing/eval sem registrar conteúdo bruto. A primeira versão não implementará WhatsApp, servidor HTTP, execução real de automações, shell livre ou agente autônomo; ela estabelecerá o núcleo racional: entrada textual, roteamento de intenção, resposta conversacional, memória efêmera, confirmação de risco e registro avaliável.

A arquitetura será modular e simples: um adaptador CLI chama um serviço de aplicação, que compõe roteador semântico, política de segurança, memória de sessão em arquivo local e cliente LLM com saída estruturada validada por Pydantic. Tools existirão apenas como contratos simulados para preparar evolução futura sem efeitos colaterais.

## Arquitetura do Sistema



### Visão Geral dos Componentes

- `alfred.cli`: componente novo responsável por receber um comando único (`alfred "pedido"`), flags operacionais (`--session`, `--json`, `--no-trace`) e imprimir saída em texto humano por padrão.
- `alfred.app.assistant_service`: componente novo que coordena o fluxo principal: montar contexto, chamar roteador, aplicar política de risco, acionar resposta direta ou tool simulada e persistir resultado avaliável.
- `alfred.routing.intent_router`: componente novo baseado em LangChain `create_agent` com `response_format` estruturado para classificar `CHITCHAT`, `CLOUD_TASK`, `LOCAL_TASK`, `AMBIGUOUS`, `BLOCKED` ou `OUT_OF_SCOPE`.
- `alfred.safety.policy`: componente novo com regras determinísticas antes/depois do LLM para detectar destrutividade, privacidade, financeiro/legal e comandos perigosos como `rm -rf`, `git push`, `git revert` e similares.
- `alfred.memory.session_store`: componente novo de memória efêmera em arquivo local, com TTL inicial de 2 horas, limpeza preguiçosa e sem memória permanente.
- `alfred.llm.openrouter_client`: componente novo para inicializar modelo via LangChain/OpenRouter usando configuração por ambiente.
- `alfred.tools.simulated_registry`: componente novo com tools declarativas sem execução real, retornando apenas intenção preparada, status e necessidade de confirmação.
- `alfred.observability.telemetry`: componente novo para LangSmith e logs locais com metadados, latência, categoria, resultado de segurança e hashes, sem prompt/resposta brutos.
- `tests/fixtures/eval_cases.*`: componente novo com dataset manual versionado e sincronização opcional com LangSmith.

Fluxo de dados: CLI normaliza entrada e `session_id`; `assistant_service` carrega contexto válido do `session_store`; `intent_router` retorna decisão estruturada; `policy` bloqueia ou exige confirmação quando necessário; o serviço gera resposta final; observabilidade registra metadados; memória recebe o resumo mínimo da interação.

## Design de Implementação



### Interfaces Principais

```python
class AssistantService(Protocol):
    def handle(self, request: AssistantRequest) -> AssistantResponse: ...

class IntentRouter(Protocol):
    def classify(self, request: AssistantRequest, context: SessionContext) -> IntentDecision: ...

class SessionStore(Protocol):
    def load(self, session_id: str) -> SessionContext: ...
    def append(self, session_id: str, turn: SessionTurn) -> None: ...
    def prune_expired(self) -> None: ...

class SafetyPolicy(Protocol):
    def evaluate(self, decision: IntentDecision, request: AssistantRequest) -> SafetyDecision: ...
```



### Modelos de Dados

- `AssistantRequest`: `message`, `session_id`, `channel="cli"`, `output_format`, `interactive_confirmation`, `trace_enabled`.
- `IntentDecision`: `category`, `confidence`, `rationale_code`, `required_clarification`, `simulated_tool_name`, `risk_labels`.
- `SafetyDecision`: `status` (`ALLOW`, `CONFIRM`, `BLOCK`), `reason_code`, `human_message`.
- `AssistantResponse`: `text`, `category`, `safety_status`, `session_id`, `metadata`, `json_payload` opcional.
- `SessionContext`: lista curta de `SessionTurn` com `created_at`, `expires_at`, `category`, `summary`, `decision_hash`; sem conteúdo bruto por padrão.
- Persistência: arquivo local em diretório de app do usuário, preferencialmente JSON Lines ou JSON compacto por sessão. O schema deve incluir versão para migração futura.



### Endpoints de API

Não aplicável ao MVP. A primeira versão não terá servidor HTTP, webhook, API pública ou endpoint de WhatsApp. Futuras integrações devem reutilizar `AssistantService` como boundary de aplicação.

## Pontos de Integração

- OpenRouter: usado como provedor LLM prioritário via LangChain. Autenticação por variável de ambiente, sem chave em arquivo versionado. Falhas devem retornar mensagem clara de indisponibilidade/configuração.
- LangSmith: tracing e datasets/evals, com política de não registrar conteúdo bruto. Traces devem conter tags, hashes, categoria, latência e status de segurança.
- Sistema local de arquivos: apenas para configuração, memória efêmera e dataset manual. Não há execução de shell livre.



## Abordagem de Testes



### Testes Unidade

- `SafetyPolicy`: bloquear categorias destrutivas, privacidade, financeiro/legal e comandos perigosos; exigir confirmação quando aplicável.
- `SessionStore`: carregar, anexar, expirar por TTL de 2 horas, limpar sessões antigas e preservar schema versionado.
- `IntentRouter`: validar parsing/contrato Pydantic usando mocks do LLM e casos de saída inválida.
- `AssistantService`: cobrir fluxo permitido, bloqueado, ambíguo, fora de escopo, confirmação interativa e saída JSON opcional.
- CLI: validar argumentos, flags, códigos de saída e renderização de texto sem depender de cor.



### Testes de Integração

- Fluxo CLI completo com LLM mockado, memória em diretório temporário e telemetry fake.
- Dataset manual de intenções com acurácia calculável, mirando a métrica de 85% do PRD.
- Integração opcional com LangSmith em ambiente configurado, sem conteúdo bruto.



### Testes de E2E

Não há frontend no MVP; Playwright não se aplica. O equivalente E2E será execução da CLI em processo real com ambiente isolado, cobrindo texto padrão e `--json`.

## Sequenciamento de Desenvolvimento



### Ordem de Construção

1. Criar estrutura Python, empacotamento e CLI mínima, pois define o ponto de entrada e a forma de uso.
2. Definir modelos Pydantic e contratos internos, pois roteamento, segurança, memória e testes dependem desses schemas.
3. Implementar `SessionStore` local com TTL, porque o serviço principal precisa de contexto curto previsível.
4. Implementar `SafetyPolicy` determinística antes de depender do LLM, reduzindo riscos desde o início.
5. Integrar LangChain/OpenRouter com resposta estruturada para classificação.
6. Implementar `AssistantService`, tools simuladas, renderização texto/JSON e prompt interativo de confirmação.
7. Adicionar observabilidade LangSmith sem conteúdo bruto, dataset de avaliação e testes de integração.



### Dependências Técnicas

- Python moderno com gerenciador `uv` recomendado para projeto, lockfile e execução local.
- Dependências prováveis: `langchain`, integração OpenRouter compatível, `pydantic`, `typer`, `platformdirs`, `pytest` e SDK/configuração LangSmith.
- Chaves: `OPENROUTER_API_KEY`; LangSmith opcional com `LANGSMITH_TRACING` e `LANGSMITH_API_KEY`.
- Disponibilidade de rede para chamadas LLM e tracing quando habilitado.



## Monitoramento e Observabilidade

O MVP usará LangSmith para tracing/eval e logs locais estruturados, evitando conteúdo bruto de mensagens. Métricas devem ser nomeadas em formato compatível com Prometheus para futura exportação, mesmo sem servidor no MVP: `alfred_requests_total`, `alfred_intent_classification_total`, `alfred_blocked_requests_total`, `alfred_confirmation_required_total`, `alfred_llm_latency_seconds`, `alfred_router_confidence`.

Logs locais devem registrar nível `INFO` para decisões normais, `WARNING` para bloqueios/confirmações e `ERROR` para falhas de provedor/configuração. Integração com Grafana não será criada no MVP; os nomes de métricas e campos de log devem facilitar um exporter futuro.

## Considerações Técnicas



### Decisões Principais

- Python + LangChain foi escolhido por simplicidade de estudo, integração com modelos e suporte a structured output.
- OpenRouter foi priorizado para permitir troca de modelos sem acoplar o domínio a um único fornecedor.
- Pydantic será usado para contratos internos e validação de saída do LLM, reduzindo parsing manual.
- Typer é a opção recomendada para CLI por tipagem, ajuda automática e baixo custo de estruturação.
- LangGraph fica fora do MVP por adicionar orquestração stateful mais poderosa do que o necessário; pode entrar quando houver workflows duráveis ou human-in-the-loop mais complexos.
- Tools simuladas substituem execução real para preservar segurança e estudar function/tool calling sem efeitos colaterais.



### Riscos Conhecidos

- Classificação LLM pode variar; mitigar com schemas estritos, dataset manual, exemplos de eval e regras determinísticas de segurança.
- Tracing pode vazar dados se mal configurado; mitigar com redaction/desativação de conteúdo bruto por padrão.
- Confirmação interativa conflita parcialmente com uso assíncrono; aceitar no MVP CLI e revisar quando WhatsApp voltar ao escopo.
- Lista de comandos perigosos nunca será completa; tratar blacklist como camada adicional, não como única barreira, e manter shell livre fora do escopo.



### Conformidade com Rules

- Nenhuma pasta de rules foi encontrada em `.agents/rules` do projeto ou em `~/.agents/rules` durante a análise. A Tech Spec assume apenas as restrições explícitas do PRD, do documento base e desta solicitação.



### Conformidade com Skills

- `alfred-core-dev-guidelines` (`.agents/skills/alfred-core-dev-guidelines/SKILL.md`): obrigatória em qualquer alteração de código — arquitetura Router First, tools estritas, KISS/YAGNI e regras de segurança.
- `create-techspec`: aplicada para gerar esta especificação a partir do PRD, após exploração, referências externas e perguntas de clarificação.
- `create-tasks`: aplicável como próximo passo para decompor esta Tech Spec em tarefas implementáveis sem iniciar código automaticamente.
- `tester`: aplicável após implementação futura para validar aderência ao PRD, Tech Spec, testes e lints.
- `resolver`: aplicável apenas se validações futuras encontrarem falhas de build, lint, testes ou comportamento.



### Arquivos relevantes e dependentes

- `BASE_DOC.md`: contexto inicial, visão do produto e decisões de alto nível.
- `tasks/prd-assistente-pessoal-alfred/prd.md`: requisitos de produto usados como fonte primária.
- `tasks/prd-assistente-pessoal-alfred/techspec.md`: este documento.
- `pyproject.toml`: futuro manifesto Python do projeto.
- `src/alfred/cli.py`: futuro adaptador CLI.
- `src/alfred/app/assistant_service.py`: futuro serviço de aplicação.
- `src/alfred/routing/intent_router.py`: futuro roteador semântico.
- `src/alfred/safety/policy.py`: futura política de segurança.
- `src/alfred/memory/session_store.py`: futura memória efêmera local.
- `src/alfred/llm/openrouter_client.py`: futura integração LLM.
- `src/alfred/tools/simulated_registry.py`: futuro registro de tools simuladas.
- `src/alfred/observability/telemetry.py`: futura camada de logs/tracing.
- `tests/`: futura suíte unitária, integração e E2E de CLI.

