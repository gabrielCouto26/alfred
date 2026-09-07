# Tarefa 6.0: Implementar servico principal de orquestracao e tools simuladas

## Visao Geral

Implementar o `AssistantService` como boundary central da aplicacao, coordenando entrada da CLI, memoria, roteamento, politica de seguranca, resposta final e tools simuladas sem efeitos colaterais. Este entregavel transforma os componentes isolados em uma experiencia funcional do MVP.

<skills>
### Conformidade com Skills

- `alfred-core-dev-guidelines` (`.agents/skills/alfred-core-dev-guidelines/SKILL.md`): obrigatoria em qualquer alteracao de codigo — arquitetura Router First, tools estritas, KISS/YAGNI e regras de seguranca.
- `execute-task`: aplicavel para implementar esta tarefa a partir deste arquivo.
- `tester`: aplicavel apos a implementacao para validar testes, lint e aderencia ao PRD/Tech Spec.
- `resolver`: aplicavel se a validacao encontrar falhas de build, lint, testes ou comportamento.
- `execute-review`: aplicavel para revisar conformidade da implementacao antes de avancar.
</skills>

<rules>
### Conformidade com Rules

- Nenhuma pasta de rules foi encontrada em `.agents/rules` do projeto ou em `~/.agents/rules` durante a analise. Aplicar as restricoes explicitas do PRD, do `BASE_DOC.md`, da `techspec.md` e desta tarefa.
</rules>

<requirements>

- Coordenar o fluxo completo entre request, contexto de sessao, roteamento, seguranca e resposta.
- Responder diretamente a conversa rapida e orientacao simples quando nao exigir tool.
- Pedir clarificacao para solicitacoes ambiguas ou com dados insuficientes.
- Sinalizar fora de escopo quando a capacidade ainda nao existir no MVP.
- Usar tools apenas como contratos simulados, sem execucao real ou efeito colateral.
- Suportar saida texto e JSON opcional conforme CLI.

</requirements>

## Subtarefas

- [ ] 6.1 Criar `AssistantService` compondo os contratos implementados nas tarefas anteriores.
- [ ] 6.2 Implementar fluxo para `CHITCHAT`, `AMBIGUOUS`, `OUT_OF_SCOPE`, `BLOCKED`, `CLOUD_TASK` e `LOCAL_TASK`.
- [ ] 6.3 Implementar registro minimo de sessao apos cada interacao elegivel, respeitando privacidade.
- [ ] 6.4 Criar registro de tools simuladas para tarefas locais e de nuvem sem efeitos colaterais.
- [ ] 6.5 Integrar confirmacao interativa de forma simples quando a politica retornar `CONFIRM`.
- [ ] 6.6 Integrar renderizacao de resposta texto e payload JSON opcional.
- [ ] 6.7 Criar testes de unidade para fluxos permitido, bloqueado, ambiguo, fora de escopo, confirmacao e erro de provedor.
- [ ] 6.8 Criar testes de integracao do fluxo completo com LLM, memoria e telemetry fake/mockados.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "alfred.app.assistant_service", "alfred.tools.simulated_registry", "Fluxo de dados" e "Sequenciamento de Desenvolvimento".
- O servico deve concentrar orquestracao, mantendo CLI fina e componentes especializados simples.
- Nao implementar automacoes reais nem ampliar a superficie de tools alem de contratos simulados.

## Criterios de Sucesso

- Uma solicitacao CLI percorre o fluxo completo e gera resposta coerente com categoria e seguranca.
- Confirmacoes, bloqueios, ambiguidades e fora de escopo sao tratados com mensagens claras.
- Tools simuladas retornam apenas intencao preparada, status e necessidade de confirmacao.
- A memoria recebe somente resumo minimo quando apropriado.
- Testes cobrem o objetivo de negocio de experiencia consistente, segura e objetiva.

## Testes da Tarefa

- [ ] Testes de unidade para todos os ramos de decisao do `AssistantService`.
- [ ] Testes de unidade para registry de tools simuladas e ausencia de efeitos colaterais.
- [ ] Testes de integracao com CLI ou adaptador chamando o servico com dependencias fake/mockadas.
- [ ] Testes E2E parciais da CLI se o fluxo ja estiver exposto de ponta a ponta neste entregavel.

## Arquivos relevantes

- `src/alfred/app/assistant_service.py`
- `src/alfred/tools/simulated_registry.py`
- `src/alfred/cli.py`
- `src/alfred/models.py`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/prd.md`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
