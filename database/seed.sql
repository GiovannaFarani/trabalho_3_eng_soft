-- Usuário Advogado padrão (Senha: Senha@123)
INSERT INTO users (id, nome_completo, email, senha_hash, cpf, tipo_perfil, numero_oab, termos_aceitos)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Dr. Fulano da Silva',
    'fulano@exemplo.com.br',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8.',
    '123.456.789-09',
    'ADVOGADO',
    '45.678 / BA',
    TRUE
);

-- Registros de exemplo cobrindo todos os estados da ADR-012 e Tela 4
INSERT INTO records (id, user_id, titulo, url_alvo, data_hora_inicio, data_hora_fim, detalhes_resumo, status)
VALUES
    ('VRD-2026-0105', '11111111-1111-1111-1111-111111111111', 'Oferta anunciada • Notebook Aurora 14', 'https://loja.orbita.example/notebook-aurora-14', '2026-10-22 10:14:00', NULL, '1 vídeo em gravação • 1 imagem • sessão ativa', 'INICIADO'),
    ('VRD-2026-0104', '11111111-1111-1111-1111-111111111111', 'Oferta anunciada • Notebook Aurora 14', 'https://loja.orbita.example/notebook-aurora-14', '2026-10-22 09:32:10', '2026-10-22 09:35:24', '1 vídeo • 4 imagens • 00:03:14 • 48.5 MB', 'CONCLUIDO'),
    ('VRD-2026-0103', '11111111-1111-1111-1111-111111111111', 'Publicação • Perfil Comercial', 'https://rede.exemplo.com.br', '2026-10-22 09:20:00', NULL, 'Gerando pacote ZIP • Verificação em andamento', 'PROCESSANDO'),
    ('VRD-2026-0102', '11111111-1111-1111-1111-111111111111', 'Condições de contratação', 'https://servicos.exemplo.com.br', '2026-10-21 16:08:03', '2026-10-21 16:09:50', '1 vídeo • 2 imagens • 00:01:47 • 22.8 MB', 'CONCLUIDO'),
    ('VRD-2026-0101', '11111111-1111-1111-1111-111111111111', 'Anúncio • Imóvel residencial', 'https://imoveis.exemplo.com.br', '2026-10-21 15:42:11', NULL, 'URL indisponível • 1 crédito devolvido', 'FALHA');
