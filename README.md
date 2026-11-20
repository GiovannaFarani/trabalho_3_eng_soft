# Veridt — Trabalho III (Engenharia de Software Aplicada)

Implementação funcional do recorte arquitetural da plataforma **Veridt** (preservação de provas digitais), cobrindo **31,25%** dos requisitos (`REQ 01`, `REQ 02`, `REQ 03`, `REQ 04` e `REQ 12`) sobre uma **Service-Based Architecture (ADR-014)**.

Para o detalhamento formal dos requisitos implementados, cálculo de cobertura e mapeamento arquitetural, consulte [`REQUISITOS_SPRINT.md`](REQUISITOS_SPRINT.md).

---

## Arquitetura do Projeto

| Componente | Diretório | Porta | Responsabilidade |
| :--- | :--- | :---: | :--- |
| **Portal Web (Frontend)** | `frontend/` | `5173` | Interface SvelteKit (Telas 1 e 4), clientes HTTP segregados (ISP) com injeção automática de `X-Correlation-ID` e `Authorization` |
| **Core & Billing Service (IAM)** | `sevices/core-service/` | `3001` | Cadastro (`REQ 01`), Recuperação de Senha (`REQ 02`), Login JWT (`REQ 03`), Logout com Blacklist (`REQ 04`) |
| **Evidence & Notification Service** | `sevices/evidence-service/` | `3002` | Listagem de registros com isolamento de tenant (`REQ 12`) + Worker RabbitMQ/SMTP com Retry e DLQ (`REQ 02`) |
| **PostgreSQL 15** | `database/` | `5432` | Banco relacional ACID compartilhado (`users`, `revoked_tokens`, `password_resets`, `records`) |
| **RabbitMQ 3 (Management)** | `docker-compose.yml` | `5672` / `15672` | Broker assíncrono (`password_recovery_queue` e `password_recovery_dlq`) |

---

## Pré-requisitos

- **Docker** e **Docker Compose**
- **Python 3.11+** (com `pip` / `venv`)
- **Node.js 20+** (ou **Bun**) para o frontend
- Uma conta gratuita no [Mailtrap.io](https://mailtrap.io/) (*Email Testing > Inboxes*) ou outro servidor SMTP de testes para o disparo de e-mails do `REQ 02`

---

## Passo a Passo para Executar Localmente

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd trabalho_3_eng_soft
```

### 2. Subir PostgreSQL e RabbitMQ com Docker

```bash
docker compose up -d
```

Na primeira inicialização, o PostgreSQL executa automaticamente:
- `database/init.sql` (criação das tabelas `users`, `revoked_tokens`, `password_resets` e `records`)
- `database/seed.sql` (usuário de teste e 5 registros cobrindo todos os estados da ADR-012)

> **Painel do RabbitMQ:** acesse `http://localhost:15672` com usuário `veridt` e senha `veridt_password`.

> **Usuário seed para login rápido:**
> - **E-mail:** `fulano@exemplo.com.br`
> - **Senha:** `Senha@123`
> - **Perfil:** `ADVOGADO` (`OAB: 45.678 / BA`)

### 3. Configurar os arquivos `.env`

Crie o `.env` de cada serviço a partir dos respectivos `.env.example`:

```bash
cp sevices/core-service/.env.example sevices/core-service/.env
cp sevices/evidence-service/.env.example sevices/evidence-service/.env
```

Verifique/ajuste as variáveis principais:
- **`JWT_SECRET`**: deve ser **idêntico** em `sevices/core-service/.env` e `sevices/evidence-service/.env` (mínimo 32 caracteres).
- **`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`** em `sevices/evidence-service/.env`: preencha com as credenciais SMTP do Mailtrap.
- **`ENABLE_EMBEDDED_CONSUMER`** em `sevices/evidence-service/.env`:
  - Defina como `true` para rodar o consumidor RabbitMQ/SMTP junto com a API do `evidence-service`, **ou**
  - Mantenha `false` e execute `python run_consumer.py` em um terminal separado (útil para acompanhar os logs do worker isoladamente).

### 4. Executar os 3 serviços (em terminais separados)

#### Terminal 1 — Core & Billing Service (porta `3001`)

```bash
cd sevices/core-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

Documentação interativa (Swagger): `http://localhost:3001/docs`

#### Terminal 2 — Evidence & Notification Service (porta `3002`)

```bash
cd sevices/evidence-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3002 --reload
```

Documentação interativa (Swagger): `http://localhost:3002/docs`

> Se `ENABLE_EMBEDDED_CONSUMER=false` no `.env` do `evidence-service`, inicie também o worker em outro terminal (com o mesmo `.venv` ativo):
> ```bash
> cd sevices/evidence-service
> python run_consumer.py
> ```

#### Terminal 3 — Portal Web / Frontend (porta `5173`)

```bash
cd frontend
npm install   # ou: bun install
npm run dev   # ou: bun run dev
```

Acesse o Portal Web em: `http://localhost:5173`

> O `vite.config.ts` já faz proxy automático de `/api/auth` → `http://localhost:3001` e `/api/records` → `http://localhost:3002`. Caso queira apontar para URLs diferentes, configure `VITE_CORE_SERVICE_URL` e `VITE_EVIDENCE_SERVICE_URL` em `frontend/.env`.

---

## Executando os Testes

### Core Service
```bash
cd sevices/core-service
pytest -v
```

### Evidence Service
```bash
cd sevices/evidence-service
pytest -v
```

### Frontend
```bash
cd frontend
npm run test        # testes unitários (Vitest)
npm run check       # verificação de tipos (svelte-check)
```

---

## Estrutura de Pastas

```text
.
├── database/
│   ├── init.sql                  # Schema PostgreSQL (users, revoked_tokens, password_resets, records)
│   └── seed.sql                  # Usuário padrão (Dr. Fulano) e 5 registros de exemplo
├── docker-compose.yml            # PostgreSQL 15 + RabbitMQ 3 (Management)
├── frontend/                     # Portal Web (SvelteKit + Tailwind + Vitest)
├── sevices/
│   ├── core-service/             # Core & Billing Service — Porta 3001 (FastAPI)
│   └── evidence-service/         # Evidence & Notification Service — Porta 3002 (FastAPI + Worker SMTP)
├── README.md                     # Este guia de execução
└── REQUISITOS_SPRINT.md          # Escopo formal, cálculo de cobertura (31,25%) e mapeamento arquitetural
```
