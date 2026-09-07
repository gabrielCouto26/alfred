# Tarefa 8.0: Consolidar fluxo E2E da CLI, documentacao minima de uso e validacao do MVP

## Visao Geral

Consolidar a primeira etapa do Alfred validando o fluxo real pela CLI, documentando uso minimo e garantindo que os objetivos principais do MVP estejam cobertos por testes automatizados. Este entregavel fecha a base inicial de desenvolvimento com foco em manutencao, seguranca e experiencia objetiva.

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

- Validar o uso real da CLI em processo completo com ambiente isolado.
- Cobrir saida texto padrao e saida `--json`.
- Documentar configuracao minima de ambiente, uso da CLI, tracing e limitacoes do MVP.
- Validar cenarios representativos de chitchat, local task, cloud task, ambiguidade, bloqueio, confirmacao e fora de escopo.
- Garantir que WhatsApp, servidor HTTP, shell livre, automacoes reais e memoria permanente continuam fora do MVP.

</requirements>

## Subtarefas

- [ ] 8.1 Criar testes E2E da CLI em processo real com dependencias externas mockadas ou desabilitadas.
- [ ] 8.2 Cobrir execucao com texto padrao, `--json`, `--session` e `--no-trace`.
- [ ] 8.3 Criar cenarios de integracao representativos dos requisitos funcionais do PRD.
- [ ] 8.4 Validar que nenhuma automacao real, shell livre ou tool com efeito colateral e executada.
- [ ] 8.5 Documentar uso local minimo, variaveis de ambiente e limitacoes explicitas do MVP.
- [ ] 8.6 Documentar como executar testes e avaliacao de intencao.
- [ ] 8.7 Executar suite automatizada completa e corrigir apenas falhas dentro do escopo da implementacao.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "Abordagem de Testes", "Sequenciamento de Desenvolvimento" e "Fora de Escopo" do PRD.
- Esta tarefa deve consolidar o que ja foi implementado, nao adicionar novas capacidades de produto.
- A documentacao deve ser minima e operacional, focada em desenvolvedor e uso local.

## Criterios de Sucesso

- A CLI funciona de ponta a ponta em ambiente isolado para os principais cenarios do PRD.
- A saida JSON e parseavel e a saida texto e legivel em terminal simples.
- A suite de testes completa passa.
- A documentacao permite instalar, configurar e executar o MVP localmente.
- O escopo negativo do MVP permanece protegido e testado.

## Testes da Tarefa

- [ ] Testes de unidade afetados pela consolidacao final, se houver ajustes de comportamento.
- [ ] Testes de integracao cobrindo cenarios representativos do PRD e pipeline de avaliacao.
- [ ] Testes E2E da CLI em processo real para texto padrao, JSON, sessao, tracing desabilitado e bloqueios de seguranca.

## Arquivos relevantes

- `src/alfred/cli.py`
- `src/alfred/app/assistant_service.py`
- `tests/e2e/`
- `tests/integration/`
- `tests/fixtures/eval_cases.*`
- `README.md`
- `tasks/prd-assistente-pessoal-alfred/prd.md`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
