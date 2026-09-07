## Documento de Requisitos de Produto (PRD)

## Visão Geral

O Alfred é um assistente pessoal baseado em IA, inspirado na persona de um mordomo polido, preciso e reativo. A primeira versão deve estabelecer um “cérebro” único capaz de receber pedidos por CLI e WhatsApp, entender a intenção do usuário e responder de forma útil, segura e consistente sem exigir uma sessão contínua de chat.

O problema principal a resolver é centralizar interações pessoais recorrentes em uma camada única de orquestração: o usuário deve conseguir enviar uma instrução curta, receber uma resposta clara e ter a intenção corretamente classificada para uso atual ou evolução futura com tools. Nesta fase, o produto não deve priorizar a execução real de automações complexas, mas sim a experiência confiável de entrada, resposta, classificação, memória curta e limites de segurança.

O valor do Alfred está em reduzir atrito para delegar intenções pessoais, criar uma base segura para múltiplas tools futuras e permitir uso assíncrono a partir de canais já naturais para o usuário: terminal e WhatsApp.

## Objetivos

- Validar que um assistente pessoal single-tenant consegue entender solicitações curtas por CLI e WhatsApp com uma experiência consistente.
- Alcançar pelo menos 85% de acerto na classificação de intenções em um conjunto de testes pessoais com pedidos reais ou simulados.
- Garantir que nenhuma ação sensível, destrutiva, privada ou de custo relevante seja tratada como autorizada sem confirmação explícita do usuário.
- Reduzir passos manuais em interações pessoais simples, especialmente quando o usuário quer registrar uma intenção, obter uma resposta rápida ou preparar uma ação futura.



## Histórias de Usuário

- Como usuário principal, eu quero enviar um pedido curto pela CLI sem abrir uma sessão longa de chat para receber uma resposta objetiva e adequada ao contexto local.
- Como usuário principal, eu quero enviar uma mensagem para um número específico no WhatsApp para interagir com o Alfred quando estiver longe do computador. (Futuro - Evolução do Produto)
- Como usuário principal, eu quero que o Alfred diferencie conversa simples, tarefa em nuvem e tarefa local para evitar respostas confusas ou ações indevidas.
- Como usuário principal, eu quero que o Alfred mantenha contexto de curto prazo dentro de uma sessão para conseguir corrigir uma solicitação anterior, como “tenta de novo com outro parâmetro”, sem repetir tudo.
- Como usuário principal, eu quero que o Alfred peça confirmação antes de qualquer ação sensível para preservar segurança, privacidade e controle.
- Como usuário principal, eu quero que o Alfred diga claramente quando uma solicitação está fora do escopo da versão atual para não criar expectativa falsa.
- Como usuário secundário indireto, representado por sistemas já existentes de WhatsApp e ambiente local, eu quero receber intenções bem delimitadas para que integrações futuras sejam previsíveis e seguras.



## Funcionalidades Principais

1. Identidade e resposta conversacional do Alfred

O Alfred deve responder com uma persona consistente: polida, precisa, reativa e direta. Essa funcionalidade é importante para tornar o assistente previsível, agradável e alinhado ao conceito do produto.

Requisitos funcionais:

RF-1. O Alfred deve responder a mensagens de conversa rápida sem exigir acionamento de tools.

RF-2. O Alfred deve manter tom educado, objetivo e profissional em todos os canais suportados.

RF-3. O Alfred deve evitar respostas longas quando o pedido do usuário for simples.

RF-4. O Alfred deve reconhecer quando não possui informação suficiente e pedir clarificação em vez de assumir dados críticos.

1. Entrada por múltiplos canais

O usuário deve conseguir acionar o Alfred por CLI e futuramente por WhatsApp. Essa funcionalidade é importante porque permite uso tanto no ambiente local de trabalho quanto em interações remotas e assíncronas.

Requisitos funcionais:

RF-5. O Alfred deve aceitar solicitações iniciadas por CLI sem depender de uma sessão interativa contínua.

RF-6. O Alfred deve aceitar solicitações originadas do fluxo existente de recebimento de mensagens por WhatsApp. (Futuro - Evolução do Produto)

RF-7. O Alfred deve preservar uma experiência consistente entre canais, mantendo diferenças apenas quando forem necessárias pelo contexto do canal.

RF-8. O Alfred deve informar ao usuário o estado básico da solicitação quando não puder entregar uma resposta final imediata.

1. Classificação de intenção e orquestração

O Alfred deve classificar cada solicitação para decidir se deve responder diretamente, preparar uma tarefa de nuvem, preparar uma tarefa local, pedir clarificação ou bloquear a solicitação. Essa funcionalidade é a base para múltiplas tools futuras sem expor capacidades amplas de forma insegura.

Requisitos funcionais:

RF-9. O Alfred deve classificar solicitações em categorias de alto nível, incluindo conversa rápida, tarefa de nuvem, tarefa local, solicitação ambígua e solicitação bloqueada.

RF-10. O Alfred deve responder diretamente quando a solicitação for conversa rápida ou orientação simples que não exija tool.

RF-11. O Alfred deve pedir clarificação quando a intenção, o canal, o risco ou os dados necessários não forem suficientes.

RF-12. O Alfred deve sinalizar claramente quando uma solicitação depende de capacidade ainda fora do escopo da versão atual.

RF-13. O Alfred deve registrar o resultado da classificação de forma avaliável para permitir medir acurácia e evolução do produto.

1. Segurança e confirmação de ações sensíveis

O Alfred deve tratar segurança como requisito central. Mesmo nesta versão de orquestração, pedidos que envolvam risco devem ser identificados e condicionados a confirmação explícita antes de qualquer evolução para execução futura.

Requisitos funcionais:

RF-14. O Alfred deve identificar solicitações potencialmente destrutivas, privadas, financeiras, legais, de credenciais ou com impacto externo.

RF-15. O Alfred deve exigir confirmação explícita do usuário antes de considerar qualquer ação sensível como autorizada.

RF-16. O Alfred deve bloquear solicitações que envolvam execução irrestrita, comandos livres não delimitados ou ações incompatíveis com as restrições do produto.

RF-17. O Alfred deve explicar de forma breve por que uma solicitação foi bloqueada ou colocada em confirmação.

1. Memória efêmera de sessão

O Alfred deve manter contexto curto o suficiente para permitir correções sequenciais sem criar memória permanente. Essa funcionalidade é importante para usabilidade, mas também preserva privacidade e reduz acúmulo de informação pessoal desnecessária.

Requisitos funcionais:

RF-18. O Alfred deve associar interações relacionadas a uma sessão temporária.

RF-19. O Alfred deve permitir referências curtas a mensagens anteriores dentro da mesma sessão, como correções ou complementos.

RF-20. O Alfred deve descartar contexto de sessão após expiração definida pelo produto.

RF-21. O Alfred não deve criar memória permanente do usuário nesta primeira versão.

## Experiência do Usuário

O usuário principal é Gabriel, usando o Alfred como assistente pessoal single-tenant. Suas necessidades principais são rapidez, previsibilidade, controle e segurança. O assistente deve funcionar como um ponto central para expressar intenções, mesmo quando a ação completa ainda não está disponível no MVP.

Na CLI, a experiência deve favorecer comandos curtos, respostas objetivas e uso sem sessão contínua. O usuário deve conseguir pedir algo e receber uma resposta final, uma pergunta de clarificação, um bloqueio justificado ou uma indicação de que a capacidade ainda não está disponível.

No WhatsApp (Futuro), a experiência deve favorecer mensagens naturais e assíncronas. O Alfred deve responder de forma clara, sem depender de formatação complexa, e deve considerar que o usuário pode estar em mobilidade, com menos tolerância a respostas longas.

Requisitos de UI/UX:

- As respostas devem usar linguagem clara, sem jargão técnico desnecessário.
- Mensagens de bloqueio ou confirmação devem ser curtas e acionáveis.
- O Alfred deve diferenciar “não posso fazer”, “ainda não está no escopo” e “preciso de mais informação”.
- O canal CLI deve priorizar saída legível em terminal.
- O canal WhatsApp deve priorizar leitura rápida em tela pequena. (Futuro)

Requisitos de acessibilidade:

- As respostas devem ser compreensíveis sem depender de cor, emojis, imagens ou formatação visual avançada.
- Mensagens devem ser úteis em leitores de tela e clientes simples de texto.
- O Alfred deve evitar ambiguidades em confirmações, especialmente para ações sensíveis.



## Restrições Técnicas de Alto Nível

- O produto será single-tenant, destinado ao uso pessoal de Gabriel, sem contas, papéis ou permissões multiusuário na primeira versão.
- O produto não deve depender de execução local de modelos de linguagem; modelos de IA utilizados devem ser serviços de nuvem.
- O produto deve interoperar com dois canais principais: CLI e o fluxo existente de recebimento e processamento de mensagens de WhatsApp. (Futuro)
- A orquestração deve considerar boas práticas de tool/function calling: capacidades bem descritas, entradas estruturadas, fronteiras claras de acionamento e possibilidade de não acionar nenhuma tool quando a resposta direta for suficiente.
- A superfície inicial de capacidades deve permanecer pequena para preservar previsibilidade, custo, latência e acurácia de roteamento.
- Solicitações sensíveis exigem confirmação explícita antes de qualquer ação que possa gerar impacto real, acesso privado, custo, modificação de dados ou execução no ambiente local.
- O contexto de curto prazo deve ter expiração, sem memória permanente no MVP.
- O produto deve ter metas observáveis de acurácia de roteamento, tempo de resposta, segurança e uso real semanal.
- Dados pessoais, conteúdo de mensagens e contexto de sessão devem ser tratados como sensíveis e minimizados ao necessário para atender à solicitação.



## Fora de Escopo

- Suporte a múltiplos usuários, times, permissões por papel ou compartilhamento de assistente.
- Interface web, painel administrativo, aplicativo mobile próprio ou qualquer UI além de CLI.
- Agentic loop, agentes autônomos, execução proativa recorrente ou tomada de iniciativa sem pedido direto do usuário.
- Memória permanente, perfil persistente do usuário ou base de conhecimento pessoal duradoura.
- Execução irrestrita de comandos, scripts livres, shell aberto ou tools sem limites claros.
- Integrações completas com agenda, e-mail, arquivos pessoais, sistemas financeiros, automação residencial ou serviços externos específicos.
- Execução efetiva de tarefas locais ou de nuvem como objetivo principal desta primeira versão, além da classificação, resposta direta, confirmação e sinalização de escopo.
- Suporte a anexos complexos, áudio, imagem, voz ou mídia rica no WhatsApp.
- Garantia de disponibilidade, escalabilidade ou observabilidade para uso público ou comercial.
- Implementar servidor de Whatsapp nesse MVP.

(Nota: Riscos de implementação técnica serão detalhados na Tech Spec.)