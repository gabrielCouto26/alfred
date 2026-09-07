# Tarefa 4.0: Implementar politica deterministica de seguranca e confirmacao

## Visao Geral

Implementar a camada deterministica de seguranca que avalia solicitacoes e decisoes de intencao para permitir, bloquear ou exigir confirmacao explicita. Este entregavel reduz risco antes de depender de classificacao LLM e preserva o controle do usuario.

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

- Identificar solicitacoes destrutivas, privadas, financeiras, legais, de credenciais ou com impacto externo.
- Bloquear execucao irrestrita, comandos livres nao delimitados e acoes fora das restricoes do produto.
- Exigir confirmacao explicita para qualquer acao sensivel antes de considera-la autorizada.
- Produzir mensagens curtas, acionaveis e compreensiveis para bloqueio ou confirmacao.
- Nao executar comandos, scripts, tools reais ou qualquer acao com efeito colateral.

</requirements>

## Subtarefas

- [ ] 4.1 Criar implementacao de `SafetyPolicy` conforme contrato definido na tarefa 2.0.
- [ ] 4.2 Definir regras deterministicas para comandos perigosos e solicitacoes explicitamente bloqueadas.
- [ ] 4.3 Definir regras para exigir confirmacao em pedidos sensiveis, privados ou de impacto externo.
- [ ] 4.4 Definir mensagens humanas curtas para `BLOCK` e `CONFIRM`.
- [ ] 4.5 Integrar classificacoes e labels de risco vindas de `IntentDecision` sem depender exclusivamente do LLM.
- [ ] 4.6 Criar testes de unidade para cenarios destrutivos, privacidade, financeiro/legal, credenciais e comandos perigosos.
- [ ] 4.7 Criar testes de integracao aplicando a politica em requests e decisoes simuladas.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "alfred.safety.policy", "Abordagem de Testes" e "Riscos Conhecidos".
- A lista de padroes perigosos deve ser camada adicional, nao autorizacao implicita para tudo que nao estiver listado.
- Confirmacao interativa sera consumida pelo servico principal em tarefa posterior.

## Criterios de Sucesso

- Solicitacoes de risco sao bloqueadas ou colocadas em confirmacao de forma previsivel.
- Pedidos simples e seguros podem ser permitidos sem friccao adicional.
- Mensagens de seguranca distinguem claramente bloqueio, confirmacao e falta de escopo.
- Testes cobrem o requisito de negocio de nao tratar acao sensivel como autorizada sem confirmacao explicita.

## Testes da Tarefa

- [ ] Testes de unidade para regras de `ALLOW`, `CONFIRM` e `BLOCK`.
- [ ] Testes de unidade para comandos perigosos citados na Tech Spec e variacoes comuns.
- [ ] Testes de integracao com `AssistantRequest` e `IntentDecision` simulados.
- [ ] Testes E2E nao aplicaveis nesta tarefa isolada; serao cobertos no fluxo CLI completo.

## Arquivos relevantes

- `src/alfred/safety/policy.py`
- `src/alfred/models.py`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/prd.md`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
