# Documento de Contexto: Assistente Pessoal "Alfred"

## 1. Visão do Produto
*   **Objetivo:** Criar um assistente pessoal para automação assíncrona, guiado pela persona do mordomo Alfred (polido, preciso e reativo).
*   **Interfaces (O Guarda-Chuva):** Um único cérebro atendendo a duas frentes distintas:
    *   **CLI (Ambiente Local):** Focado em execução de bash/scripts locais via terminal Zsh. A IA atua como tradutora de intenções para ações no sistema operacional.
    *   **WhatsApp (Nuvem):** Focado em serviços web (pesquisas, leitura de documentos, integrações). 
*   **Metodologia:** Spec Driven Development (SDD). Este documento servirá de base para a criação do PRD e da TechSpec.

## 2. Decisões Arquiteturais e Tech Stack
*   **Descartado:** Execução de LLMs localmente (foco em nuvem para economia de recursos) e complexidade de múltiplos usuários (foco em single-tenant).
*   **Cérebro Compartilhado:** Modelos de nuvem eficientes em *Function Calling* atuarão como orquestradores centrais.
*   **Separação Nuvem vs. Local:**
    *   **Nuvem:** Webhooks recebidos via Evolution API, orquestrados através do n8n e serviços em Express, acessando exclusivamentes *Cloud Tools*.
    *   **Local:** Um wrapper local (escrito em TypeScript ou Python) envia o contexto para a nuvem, recebe o *Tool Call* validado em JSON, executa a ação local no Linux e retorna os logs de saída.

## 3. Fluxos de Interação e Controle de Estado
*   **Router Semântico:** Uma camada inicial ultra-rápida classifica a intenção da mensagem (`CHITCHAT`, `CLOUD_TASK`, `LOCAL_TASK`). Isso define quais ferramentas carregar no LangChain, reduzindo latência e consumo de tokens.
*   **Ferramentas Tipadas:** Scripts não terão execução livre. Todas as ações serão mapeadas como funções estritas com *schemas* de parâmetros para evitar execuções acidentais.
*   **Memória Efêmera e Correção:** O estado será controlado por `session_id` (ex: `gabriel-cli-workspace-1`) com um limite de tempo (TTL). Isso garante o contexto de curto prazo necessário para corrigir falhas sequenciais (ex: "tenta de novo com a flag -f") sem acumular lixo informacional.
