# Alfred - Assistente Pessoal

Assistente pessoal baseado em IA para automação assíncrona, guiado pela persona do mordomo Alfred.

## Visão Geral

O Alfred é um assistente pessoal single-tenant que atende por CLI e WhatsApp, com capacidade de classificar intenções, responder conversacionalmente e coordenar tarefas em nuvem ou localmente.

## Instalação

```bash
pip install -e .
```

## Uso

```bash
alfred "sua mensagem aqui"
alfred "sua mensagem" --session minha-sessao
alfred "sua mensagem" --json
alfred "sua mensagem" --no-trace
```

## Estrutura do Projeto

```
src/alfred/
├── __init__.py
├── cli.py          # Adaptador CLI
├── models.py       # Modelos Pydantic
├── config.py       # Configurações
├── exceptions.py   # Exceções customizadas
├── exit_codes.py   # Códigos de saída
├── app/            # Camada de aplicação
├── routing/        # Roteamento de intenções
├── safety/         # Política de segurança
├── memory/         # Memória de sessão
├── llm/            # Integração LLM
├── tools/          # Tools simuladas
└── observability/  # Logging e tracing

tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
├── e2e/            # Testes E2E
└── fixtures/       # Fixtures de teste
```

## Requisitos

- Python >= 3.11
- OPENROUTER_API_KEY (variável de ambiente)

## Licença

MIT
