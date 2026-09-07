# Tarefa 3.0: Implementar memoria efemera de sessao com TTL

## Visao Geral

Implementar armazenamento local de sessao temporaria para permitir contexto curto entre interacoes relacionadas, com expiracao automatica e sem memoria permanente. Este entregavel atende a necessidade de correcoes sequenciais sem acumular informacao pessoal.

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

- Persistir contexto curto por `session_id` em arquivo local de usuario.
- Aplicar TTL inicial de 2 horas, conforme Tech Spec.
- Fazer limpeza preguiçosa de sessoes expiradas.
- Persistir apenas resumo minimo, categoria, timestamps e hash/identificador de decisao, sem conteudo bruto por padrao.
- Manter schema versionado para evolucao futura.

</requirements>

## Subtarefas

- [ ] 3.1 Criar implementacao de `SessionStore` local conforme contrato definido na tarefa 2.0.
- [ ] 3.2 Implementar `load`, `append` e `prune_expired` com comportamento previsivel quando nao houver sessao existente.
- [ ] 3.3 Implementar TTL de 2 horas e descarte de contexto expirado.
- [ ] 3.4 Garantir persistencia em diretorio de app do usuario com opcao de override para testes.
- [ ] 3.5 Garantir que conteudo bruto de mensagens nao seja persistido por padrao.
- [ ] 3.6 Criar testes de unidade para carregar, anexar, expirar, limpar e validar schema.
- [ ] 3.7 Criar testes de integracao com diretorio temporario preservando contexto entre chamadas.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "alfred.memory.session_store", "Modelos de Dados" e "Abordagem de Testes".
- A memoria deve ser simples e local, sem banco de dados ou dependencia externa.
- A implementacao deve favorecer privacidade e minimizacao de dados.

## Criterios de Sucesso

- Uma sessao recem-criada pode receber turns e ser carregada novamente.
- Turns expirados nao influenciam novas respostas.
- A limpeza preguiçosa remove ou ignora dados vencidos sem exigir job externo.
- O schema persistido possui versao.
- Testes demonstram que referencias curtas podem usar contexto valido sem criar memoria permanente.

## Testes da Tarefa

- [ ] Testes de unidade para `load`, `append`, TTL, expiracao, limpeza e schema versionado.
- [ ] Testes de integracao usando diretorio temporario e multiplas chamadas simuladas na mesma sessao.
- [ ] Testes E2E nao aplicaveis nesta tarefa isolada; serao cobertos no fluxo CLI completo.

## Arquivos relevantes

- `src/alfred/memory/session_store.py`
- `src/alfred/models.py`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
