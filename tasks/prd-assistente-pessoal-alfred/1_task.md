# Tarefa 1.0: Inicializar estrutura Python, empacotamento e CLI minima

## Visao Geral

Criar a base executavel do projeto Alfred em Python, incluindo empacotamento, estrutura inicial de pacotes, comando CLI minimo e configuracao de testes. Este entregavel estabelece o ponto de entrada do MVP sem implementar ainda a orquestracao completa.

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

- Criar uma estrutura Python simples e preparada para evoluir conforme `techspec.md`.
- Disponibilizar um comando CLI para receber uma solicitacao unica, sem exigir sessao interativa continua.
- Suportar flags operacionais iniciais previstas na Tech Spec, incluindo sessao, JSON e tracing desabilitado.
- Manter saida padrao legivel em terminal, sem dependencia de cor, emoji ou formatacao visual avancada.
- Nao implementar WhatsApp, servidor HTTP, execucao real de automacoes, shell livre ou agente autonomo.

</requirements>

## Subtarefas

- [ ] 1.1 Criar manifestos e configuracoes minimas do projeto Python conforme dependencias previstas na Tech Spec.
- [ ] 1.2 Criar a estrutura inicial de pacotes sob `src/alfred/` com modulos vazios ou placeholders seguros para os componentes principais.
- [ ] 1.3 Implementar o adaptador CLI minimo para aceitar mensagem, `--session`, `--json` e `--no-trace`.
- [ ] 1.4 Definir codigos de saida e mensagens basicas para sucesso, erro de entrada e erro de configuracao.
- [ ] 1.5 Configurar a estrutura inicial de testes automatizados.
- [ ] 1.6 Criar testes de unidade para parsing de argumentos, flags e validacoes basicas da CLI.
- [ ] 1.7 Criar testes de integracao executando a CLI em processo real com ambiente isolado.

## Detalhes de Implementacao

- Referenciar `techspec.md` nas secoes "Visao Geral dos Componentes", "Sequenciamento de Desenvolvimento" e "Dependencias Tecnicas".
- A CLI deve ser apenas o boundary de entrada; regras de negocio devem ficar fora dela para preservar manutencao.
- Nao adicionar capacidades alem das previstas para o MVP.

## Criterios de Sucesso

- O projeto pode ser instalado/executado localmente pelo gerenciador definido.
- O comando CLI aceita uma mensagem curta e responde com uma saida controlada, mesmo que ainda seja uma resposta minima.
- As flags iniciais sao reconhecidas e testadas.
- A suite de testes inicial executa com sucesso.
- Nenhum codigo permite execucao livre de comandos ou automacoes reais.

## Testes da Tarefa

- [ ] Testes de unidade para parsing de argumentos, flags, mensagens obrigatorias e codigos de erro.
- [ ] Testes de integracao para execucao da CLI em processo real com ambiente temporario.
- [ ] Testes E2E iniciais da CLI para saida texto padrao e `--json`, se o formato JSON minimo ja estiver disponivel neste entregavel.

## Arquivos relevantes

- `pyproject.toml`
- `src/alfred/__init__.py`
- `src/alfred/cli.py`
- `tests/`
- `tasks/prd-assistente-pessoal-alfred/techspec.md`
