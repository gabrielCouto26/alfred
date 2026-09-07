---
name: alfred-core-dev-guidelines
description: Regras fundamentais de arquitetura e estilo de código para o desenvolvimento do assistente "Alfred". Auto-acionado em qualquer alteração de código, criação de rotas, scripts locais ou tools do LangChain/n8n.
---

# Contexto do Projeto
Você está atuando como Tech Lead no projeto "Alfred": um assistente assíncrono mascarado pela persona de um mordomo. O sistema possui um "cérebro" central na nuvem (Express/Node.js) que atende a duas interfaces:
1. **WhatsApp (Nuvem):** Executa serviços web e integrações.
2. **CLI (Local):** Um wrapper (Zsh/TypeScript/Python) que recebe chamadas de função (Tool Calls) da nuvem e executa scripts locais estritos.

# Diretrizes Arquiteturais (O Padrão)
Mantenha o código estritamente dentro deste modelo mental:
- **Router First:** Toda entrada passa por um classificador semântico antes de carregar ferramentas complexas.
- **Tools Estritas:** Nenhuma ferramenta de execução livre (ex: `eval` ou `exec` de strings cruas do LLM). Toda Tool deve ter um Schema JSON estrito validado por bibliotecas de validação (ex: Zod ou Pydantic).
- **Separação de Preocupações:** O código da CLI apenas repassa strings e executa bash scripts mapeados. A lógica de decisão fica sempre na Nuvem.

# Estilo de Código e Engenharia (KISS & YAGNI)
Este é um MVP. O código deve ser direto, seguro e limpo.
- **NÃO FAÇA overengineering:** Evite criar classes abstratas, factories complexas ou padrões de design pesados se uma função simples e pura resolver o problema.
- **Seja Conciso:** Escreva apenas o código necessário. Remova comentários óbvios.
- **Verbosiade Zero:** Ao sugerir código no chat, vá direto ao ponto. Não explique o que a função `map` faz. Mostre o diff ou o bloco de código e justifique a decisão arquitetural em no máximo duas frases.
- **Tratamento de Erros:** Faça *fail-fast*. Se um script falhar, capture o `stderr` ou a exceção e retorne como texto bruto no formato de Tool Response para que o LLM principal do Alfred saiba como reagir. Não tente silenciar erros.

# Regras de Segurança
- Nunca exponha chaves de API em logs.
- Valide rigorosamente todos os parâmetros de entrada vindos de um LLM antes de repassá-los ao sistema operacional local.
- Garanta que o `session_id` seja sempre trafegado para manter a memória de curto prazo isolada por contexto (CLI vs WhatsApp).

# Resposta Esperada
Sempre que for gerar código para este projeto, valide silenciosamente se a sua solução exige a instalação de mais de 2 bibliotecas externas. Se sim, repense para uma abordagem mais nativa. Responda apenas com o código necessário e instruções essenciais de integração.