# Tarefa 2.0: Definir contratos internos e modelos Pydantic do dominio

## Visao Geral

Definir os modelos e contratos internos que serao usados pelos componentes do Alfred: request, response, decisao de intencao, decisao de seguranca e contexto de sessao. Este entregavel cria a linguagem comum do sistema antes da implementacao dos fluxos dependentes.

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

- Criar modelos Pydantic para os contratos descritos na Tech Spec.
- Representar categorias de intencao, status de seguranca, canais suportados e formatos de saida de forma tipada.
- Incluir campos necessarios para avaliacao posterior sem persistir conteudo bruto desnecessario.
- Preparar schema versionado para dados persistidos de sessao.
- Evitar acoplamento direto entre modelos de dominio e provedor LLM.

</requirements>

## Subtarefas

- [ ] 2.1 Criar modelos para `AssistantRequest` e `AssistantResponse`.
- [ ] 2.2 Criar modelos para `IntentDecision` com categorias previstas no PRD e Tech Spec.
- [ ] 2.3 Criar modelos para `SafetyDecision` e status `ALLOW`, `CONFIRM` e `BLOCK`.
- [ ] 2.4 Criar modelos para `SessionContext` e `SessionTurn` com schema versionado e sem conteudo bruto por padrao.
- [ ] 2.5 Definir protocolos/interfaces internos para servico, roteador, memoria e politica de seguranca.
- [ ] 2.6 Criar testes de unidade para validacao, defaults, enumeracoes e rejeicao de dados invalidos.
- [ ] 2.7 Criar testes de integracao garantindo que os contratos trafegam corretamente entre componentes fake.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "Interfaces Principais" e "Modelos de Dados".
- Os modelos devem expressar os contratos, nao regras complexas de negocio.
- O desenho deve manter a possibilidade de reutilizar `AssistantService` por canais futuros sem implementar WhatsApp neste MVP.

## Criterios de Sucesso

- Todos os contratos principais existem, sao tipados e possuem validacao automatica.
- Categorias e status aceitos estao alinhados ao PRD e a Tech Spec.
- Dados invalidos sao rejeitados de forma previsivel.
- Os modelos permitem serializacao segura para saida JSON e persistencia minima.
- Testes cobrem o objetivo de negocio de previsibilidade e seguranca de fronteiras.

## Testes da Tarefa

- [ ] Testes de unidade para criacao, validacao, serializacao e rejeicao de payloads invalidos.
- [ ] Testes de integracao com componentes fake usando os contratos em conjunto.
- [ ] Testes E2E nao aplicaveis nesta tarefa, exceto se algum contrato for exposto diretamente pela CLI ja existente.

## Arquivos relevantes

- `src/alfred/models.py`
- `src/alfred/contracts.py`
- `tests/unit/`
- `tests/integration/`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
