CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabela de Usuários (REQ 01, Apêndice A e Decisão D1)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    tipo_perfil VARCHAR(20) NOT NULL CHECK (tipo_perfil IN ('ADVOGADO', 'USUARIO_COMUM')),
    numero_oab VARCHAR(30),
    termos_aceitos BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blacklist de Tokens JWT revogados no Logout (REQ 04 e ADR-005)
CREATE TABLE revoked_tokens (
    token TEXT PRIMARY KEY,
    expires_at TIMESTAMP NOT NULL
);

-- Tokens temporários de Recuperação de Senha (REQ 02)
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reset_token VARCHAR(100) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Registros Realizados (REQ 12, Apêndice A e Máquina de Estados ADR-012)
CREATE TABLE records (
    id VARCHAR(20) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    titulo VARCHAR(200) NOT NULL,
    url_alvo VARCHAR(300) NOT NULL,
    data_hora_inicio TIMESTAMP NOT NULL,
    data_hora_fim TIMESTAMP,
    detalhes_resumo VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('INICIADO', 'PROCESSANDO', 'CONCLUIDO', 'FALHA'))
);
