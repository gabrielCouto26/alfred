# Tarefa 7.0: Implementar observabilidade segura com logs locais e LangSmith opcional

## Visao Geral

Implementar uma camada de observabilidade que registre metadados uteis para debug e avaliacao sem vazar prompt, resposta bruta ou dados pessoais desnecessarios. Este entregavel permite acompanhar uso, seguranca, latencia e classificacao mantendo privacidade como padrao.

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

- Registrar metadados de execucao, categoria, status de seguranca, latencia e hashes sem conteudo bruto.
- Suportar LangSmith de forma opcional e segura, controlada por configuracao de ambiente.
- Produzir logs locais estruturados em niveis apropriados.
- Usar nomes de metricas previstos na Tech Spec para facilitar exportacao futura.
- Permitir desativar tracing pela flag operacional prevista na CLI.

</requirements>

## Subtarefas

- [ ] 7.1 Criar camada `telemetry` para logs locais estruturados e eventos de rastreio.
- [ ] 7.2 Implementar sanitizacao/redaction para impedir registro de prompt e resposta brutos.
- [ ] 7.3 Implementar hashes ou identificadores seguros para correlacao sem expor conteudo.
- [ ] 7.4 Integrar LangSmith opcional quando ambiente estiver configurado.
- [ ] 7.5 Integrar telemetry ao `AssistantService` e respeitar `--no-trace`.
- [ ] 7.6 Criar testes de unidade para redaction, campos obrigatorios e nomes de metricas.
- [ ] 7.7 Criar testes de integracao garantindo que eventos emitidos nao contem conteudo bruto.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "alfred.observability.telemetry", "Pontos de Integracao" e "Monitoramento e Observabilidade".
- Grafana/exporter nao fazem parte deste MVP.
- Observabilidade nao deve ser requisito para o fluxo funcionar; falhas de tracing devem degradar com seguranca.

## Criterios de Sucesso

- Eventos contem metadados suficientes para avaliar classificacao, seguranca e latencia.
- Prompt e resposta brutos nao aparecem em logs ou traces por padrao.
- LangSmith e tracing local podem ser desligados sem quebrar a CLI.
- Nomes de metricas seguem os campos definidos na Tech Spec.
- Testes protegem o objetivo de negocio de avaliacao sem vazamento de dados pessoais.

## Testes da Tarefa

- [ ] Testes de unidade para redaction, hashing, campos de eventos e metricas nomeadas.
- [ ] Testes de unidade para tracing desabilitado e falha segura de provedor de telemetry.
- [ ] Testes de integracao com telemetry fake verificando ausencia de conteudo bruto.
- [ ] Testes E2E nao obrigatorios nesta tarefa isolada; serao cobertos na consolidacao do fluxo CLI.

## Arquivos relevantes

- `src/alfred/observability/telemetry.py`
- `src/alfred/app/assistant_service.py`
- `src/alfred/cli.py`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/prd.md`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
