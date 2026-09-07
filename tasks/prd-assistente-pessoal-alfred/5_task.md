# Tarefa 5.0: Implementar roteador de intencao com saida estruturada e dataset avaliavel

## Visao Geral

Implementar o roteador semantico que classifica mensagens nas categorias do MVP com saida estruturada validada. Este entregavel cria a base mensuravel para atingir a meta de acuracia de intencao e separar conversa, tarefas, ambiguidade, bloqueio e fora de escopo.

<skills>
### Conformidade com Skills

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

- Classificar solicitacoes em `CHITCHAT`, `CLOUD_TASK`, `LOCAL_TASK`, `AMBIGUOUS`, `BLOCKED` e `OUT_OF_SCOPE`.
- Retornar decisao estruturada compativel com os modelos Pydantic.
- Usar cliente LLM configuravel via OpenRouter, com possibilidade de mock nos testes.
- Registrar resultado de classificacao de forma avaliavel, sem depender de conteudo bruto persistente.
- Criar dataset manual de avaliacoes para medir acuracia, mirando o objetivo de 85% do PRD.

</requirements>

## Subtarefas

- [ ] 5.1 Criar cliente OpenRouter/LangChain configuravel por variavel de ambiente.
- [ ] 5.2 Criar `IntentRouter` com saida estruturada validada pelos contratos da tarefa 2.0.
- [ ] 5.3 Definir comportamento claro para falha de configuracao, indisponibilidade de provedor e saida invalida do LLM.
- [ ] 5.4 Criar dataset manual versionado de casos de intencao representativos do PRD.
- [ ] 5.5 Criar calculo local de acuracia do dataset para acompanhar a meta de 85%.
- [ ] 5.6 Criar testes de unidade com LLM mockado, incluindo saidas validas e invalidas.
- [ ] 5.7 Criar testes de integracao executando o dataset com roteador mockado ou deterministico para validar o pipeline de avaliacao.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "alfred.routing.intent_router", "alfred.llm.openrouter_client", "Abordagem de Testes" e "Pontos de Integracao".
- O roteador deve preparar a evolucao para tools futuras, mas nao executar nenhuma tool real.
- O dataset deve ser objetivo e pequeno o suficiente para manutencao inicial.

## Criterios de Sucesso

- O roteador retorna sempre uma decisao estruturada ou erro tratado.
- Todas as categorias previstas estao cobertas por casos de teste.
- O dataset manual permite medir acuracia de classificacao de forma reproduzivel.
- Falhas de LLM/configuracao geram mensagens claras e nao causam execucao insegura.
- Testes protegem o objetivo de negocio de classificacao confiavel e evolutiva.

## Testes da Tarefa

- [ ] Testes de unidade para parsing Pydantic, categorias, confidence, rationale e saida invalida do LLM.
- [ ] Testes de unidade para falhas de configuracao do OpenRouter.
- [ ] Testes de integracao para pipeline do dataset e calculo de acuracia.
- [ ] Testes E2E nao aplicaveis nesta tarefa isolada; serao cobertos no fluxo CLI completo.

## Arquivos relevantes

- `src/alfred/routing/intent_router.py`
- `src/alfred/llm/openrouter_client.py`
- `src/alfred/models.py`
- `tests/fixtures/eval_cases.*`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/prd.md`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
