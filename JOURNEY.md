# Nautilus Agentic Protocol
**Status:** active
**Stage:** Caminho fundador preparado para Builder

## Description

Nautilus Agentic Protocol é o corpo formal, portável e executável da gramática Nautilus. Ele representa a linguagem do método em documentos, schemas, comandos, eventos, políticas e compatibilidades sem depender de um Harness específico nem das tabelas internas do Mirror.

## Current focus

Definir o envelope mínimo do protocolo para que os quatro corpos reconheçam a mesma identidade. A primeira entrega deve declarar nome, versão do método, versão do protocolo e versão do schema, sem pretender modelar toda a ontologia.

## Builder path

O protocolo deve nascer como contrato de reconhecimento, não como banco de dados vivo. YAML funciona como formato declarativo e de intercâmbio. O estado operacional pertence ao runtime.

A primeira fatia deve validar a correspondência com o método: os termos fundadores existem como vocabulário ou metadados rastreáveis, mas apenas o mínimo necessário precisa ser formalizado. O protocolo deve conseguir dizer: isto é Nautilus, nesta versão, compatível com este schema, sustentando esta gramática experimental.

A decisão nominal da exploração vale aqui com mais força. Participante é categoria canônica. Natureza distingue humano e agêntico. Papel e Autoridade podem aparecer como campos ou extensões futuras, mas não precisam ser expandidos antes de serem testados nos casos canônicos.

## Near slice

Criar um schema mínimo e um documento YAML válido que declare a identidade Nautilus. Acrescentar fixture de exemplo e teste de conformidade que prove que o documento pode ser carregado e reconhecido sem mutação. O protocolo deve ser legível por Mirror Extension e Harness na mesma fatia vertical.

## Scope

Inclui:

- envelope de metadados do protocolo;
- schema mínimo;
- documento YAML de exemplo;
- fixture compartilhada;
- testes de validade e compatibilidade;
- vocabulário formal mínimo alinhado ao método.

Fora de escopo por padrão:

- usar YAML como persistência viva;
- depender do banco ou dos modelos internos do Mirror;
- formalizar toda a ontologia antes dos testes narrativos;
- resolver comandos e eventos além do necessário para reconhecimento.

## Done condition

A primeira iteração estará pronta quando um documento mínimo e válido declarar nome e versões, passar pelo schema e puder ser reconhecido, sem mutação, pela extensão Mirror e pelo Harness.
