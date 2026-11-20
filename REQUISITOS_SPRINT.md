# Requisitos Implementados na Sprint — Veridt (Trabalho III)

Este documento formaliza o recorte funcional implementado no **Trabalho III** da plataforma **Veridt**, comprovando o atendimento à meta mínima de cobertura (**≥ 30%**) dos requisitos especificados em [`veridit-req.pdf`](frontend/guides/veridit-req.pdf) e o alinhamento com a arquitetura definida no Trabalho II ([`Trabalho_II_ESA.pdf`](frontend/guides/Trabalho_II_ESA.pdf)).

---

## 1. Cálculo de Cobertura de Requisitos

O documento de requisitos (`veridit-req.pdf`) especifica **16 requisitos funcionais** (numerados de `REQ 01` a `REQ 15`, com dois requisitos distintos sob a numeração `REQ 11`: *Concluir captura de Tela* e *Confirmar captura de tela por email*).

| Métrica | Valor |
| :--- | :---: |
| Total de requisitos funcionais especificados | **16** |
| Requisitos implementados nesta sprint | **5** (`REQ 01`, `REQ 02`, `REQ 03`, `REQ 04`, `REQ 12`) |
| **Percentual de cobertura** | **5 / 16 = 31,25%** |
| Meta mínima exigida | **≥ 30%** (**Atendida**) |

$$\text{Cobertura} = \frac{5}{16} \times 100\% = 31{,}25\% \ge 30\%$$

---

## 2. Mapeamento dos Requisitos Implementados à Arquitetura

A solução segue o estilo **Service-Based Architecture (ADR-014)** com serviços independentes compartilhando um banco de dados relacional ACID (**PostgreSQL**) e mensageria assíncrona (**RabbitMQ**):

| REQ | Nome do Requisito | Serviços / Componentes Responsáveis | Endpoints / Fluxos | ADRs & Decisões Aplicadas |
| :--- | :--- | :--- | :--- | :--- |
| **REQ 01** | **Cadastrar Usuário** | • **Portal Web (`frontend`)**: Tela 1 (`src/routes/login/+page.svelte`) e `AuthRegisterClient` (`src/lib/api/coreAuthClient.ts`)<br>• **Core & Billing Service (`core-service`, porta 3001)**: `auth_router.py`, `auth_service.py`, `user_repository.py`<br>• **PostgreSQL**: tabela `users` | `POST /api/auth/register`<br>Valida aceite dos termos (LGPD), senha forte (8+ caracteres, letras, números e símbolos), CPF válido (11 dígitos, único), e-mail único e OAB obrigatória apenas para `ADVOGADO`. | **Decisão D1** (OAB obrigatória só para Advogado), **Apêndice A**, **ADR-009** (Correlation ID e logs JSON), **ADR-014** |
| **REQ 02** | **Recuperar Senha** | • **Portal Web (`frontend`)**: Tela 1 (`src/routes/login/+page.svelte`), rota `/reset-password` e `PasswordRecoveryClient`<br>• **Core & Billing Service (`core-service`, porta 3001)**: `password_recovery_router.py`, `password_recovery_service.py`, `password_reset_repository.py`, `rabbitmq_publisher.py`<br>• **RabbitMQ**: fila `password_recovery_queue` + `password_recovery_dlq`<br>• **Evidence & Notification Service (`evidence-service`, porta 3002)**: `rabbitmq_consumer.py`, `password_recovery_handler.py`, `email_sender.py` (SMTP/Mailtrap)<br>• **PostgreSQL**: tabelas `password_resets` e `users` | `POST /api/auth/forgot-password` (gera token com expiração de 15 min e publica na fila RabbitMQ)<br>`POST /api/auth/reset-password` (valida token não utilizado/não expirado, política de senha forte e atualiza `senha_hash`) | **ADR-005** (expiração curta de token), **ADR-007** (mensageria assíncrona com Retry e DLQ + envio SMTP), **ADR-008**, **ADR-009** (propagação de `correlationId` via fila) |
| **REQ 03** | **Logar no Sistema** | • **Portal Web (`frontend`)**: Tela 1 (`src/routes/login/+page.svelte`), `AuthLoginClient` e `authSession` (`src/lib/auth/session.svelte.ts`)<br>• **Core & Billing Service (`core-service`, porta 3001)**: `auth_router.py`, `auth_service.py`, `jwt_issuer.py`, `password_hasher.py`<br>• **PostgreSQL**: tabela `users` | `POST /api/auth/login`<br>Verifica credenciais com `bcrypt` (com proteção contra enumeração por tempo de resposta) e emite JWT assinado contendo `sub`, `nome`, `email`, `role` e `oab`. | **ADR-005** (autenticação stateless via JWT), **ADR-010** (RBAC), **ADR-009** |
| **REQ 04** | **Sair do Sistema** | • **Portal Web (`frontend`)**: barra superior da Tela 4 (`src/routes/(workspace)/+layout.svelte`) e `AuthLogoutClient`<br>• **Core & Billing Service (`core-service`, porta 3001)**: `auth_router.py`, `auth_service.py`, `revoked_token_repository.py`<br>• **Validação compartilhada (`core-service` e `evidence-service`)**: `security/auth.py` e `security/token_blacklist.py`<br>• **PostgreSQL**: tabela `revoked_tokens` | `POST /api/auth/logout`<br>Insere o token JWT na blacklist (`revoked_tokens`) até sua expiração e limpa a sessão local no Portal Web. Requisições posteriores com o token revogado retornam HTTP `401`. | **ADR-005** (blacklist de tokens JWT revogados no logout), **ADR-009** |
| **REQ 12** | **Listar Registros Realizados** | • **Portal Web (`frontend`)**: Tela 4 (`src/routes/(workspace)/records/+page.svelte`) e `RecordsReaderClient` (`src/lib/api/evidenceRecordsClient.ts`)<br>• **Evidence & Notification Service (`evidence-service`, porta 3002)**: `records/routes.py`, `security/auth.py`<br>• **PostgreSQL**: tabela `records` | `GET /api/records/`<br>Extrai `user_id` exclusivamente do JWT (`sub`), garantindo isolamento de tenant. Exibe os 4 cards de indicadores, busca por título/URL/ID, filtro por status, filtro por período e tabela com as colunas do Apêndice A. | **ADR-010** (isolamento de tenant no banco), **ADR-012** (máquina de estados: `INICIADO`, `PROCESSANDO`, `CONCLUIDO`, `FALHA`), **Apêndice A**, **ADR-009** |

---

## 3. Quadro Geral dos 16 Requisitos (Escopo da Sprint)

| # | Requisito | Status na Sprint |
| :-: | :--- | :---: |
| 1 | **REQ 01** – Cadastrar Usuário | **Implementado** |
| 2 | **REQ 02** – Recuperar Senha | **Implementado** |
| 3 | **REQ 03** – Logar no Sistema | **Implementado** |
| 4 | **REQ 04** – Sair do Sistema | **Implementado** |
| 5 | **REQ 05** – Comprar Créditos | Fora do escopo |
| 6 | **REQ 06** – Efetuar Pagamento de Créditos | Fora do escopo |
| 7 | **REQ 07** – Confirmar pagamento por email | Fora do escopo |
| 8 | **REQ 08** – Iniciar Registro de conteúdo | Fora do escopo |
| 9 | **REQ 09** – Concluir gravação de conteúdo | Fora do escopo |
| 10 | **REQ 10** – Confirmar gravação de conteúdo por email | Fora do escopo |
| 11 | **REQ 11 (a)** – Concluir captura de Tela | Fora do escopo |
| 12 | **REQ 11 (b)** – Confirmar captura de tela por email | Fora do escopo |
| 13 | **REQ 12** – Listar Registros realizados | **Implementado** |
| 14 | **REQ 13** – Visualizar Detalhes dos Registros realizados | Fora do escopo |
| 15 | **REQ 14** – Gerar Relatório do Registro realizado | Fora do escopo |
| 16 | **REQ 15** – Gerar Arquivo zip do Registro realizado | Fora do escopo |

---

## 4. Princípios SOLID Aplicados por Componente

| Princípio | Serviço / Camada | Onde está no código | Problema resolvido |
| :--- | :--- | :--- | :--- |
| **SRP** (Single Responsibility) | `core-service` (Autenticação) | `app/routers/auth_router.py`, `app/services/auth_service.py`, `app/repositories/user_repository.py` | Separa tradução HTTP, regras de negócio (LGPD, senha forte, OAB/D1, CPF único) e acesso SQL em camadas independentes. |
| **DIP** (Dependency Inversion) | `core-service` (Recuperação de Senha) | `app/services/password_recovery_service.py`, `app/messaging/publisher.py`, `app/messaging/rabbitmq_publisher.py` | O serviço de recuperação depende da abstração `IMessagePublisher`, desacoplando a regra de negócio do RabbitMQ (`pika`). |
| **OCP** (Open/Closed) | `evidence-service` (Notificações) | `app/notifications/rabbitmq_consumer.py`, `app/notifications/password_recovery_handler.py`, `app/notifications/email_sender.py` | O consumidor RabbitMQ delega o processamento a um handler injetado (`handle(payload)`), permitindo adicionar novos fluxos de notificação sem alterar a lógica de consumo, retry e DLQ. |
| **ISP** (Interface Segregation) | `frontend` (Clientes HTTP) | `src/lib/api/httpClient.ts` (`HttpGetClient`, `HttpPostClient`), `src/lib/api/coreAuthClient.ts` (`AuthLoginClient`, `AuthRegisterClient`, `AuthLogoutClient`, `PasswordRecoveryClient`), `src/lib/api/evidenceRecordsClient.ts` (`RecordsReaderClient`) | Clientes separados por serviço de domínio (`core-service` e `evidence-service`) e contratos enxutos por caso de uso, ambos injetando automaticamente `X-Correlation-ID` e `Authorization`. |
