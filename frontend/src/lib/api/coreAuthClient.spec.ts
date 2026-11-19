import { describe, expect, it, vi } from 'vitest';
import {
	createAuthLoginClient,
	createAuthLogoutClient,
	createAuthRegisterClient,
	createPasswordRecoveryClient,
	formatCpf,
	isStrongPassword
} from './coreAuthClient.ts';
import { ApiError, CORRELATION_ID_HEADER, createHttpClient } from './httpClient.ts';

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
	return new Response(JSON.stringify(body), {
		status: 200,
		headers: {
			'content-type': 'application/json',
			...init.headers
		},
		...init
	});
}

describe('createHttpClient & PasswordRecoveryClient (ISP)', () => {
	it('injects X-Correlation-ID and calls POST /api/auth/forgot-password', async () => {
		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			jsonResponse(
				{
					message:
						'Se o e-mail informado estiver cadastrado, as instruções de recuperação foram enviadas.'
				},
				{
					headers: {
						'content-type': 'application/json',
						[CORRELATION_ID_HEADER]: 'corr-123'
					}
				}
			)
		);

		const httpClient = createHttpClient({
			baseUrl: 'http://localhost:3001',
			generateCorrelationId: () => 'corr-123',
			fetchFn
		});
		const client = createPasswordRecoveryClient(httpClient);

		const result = await client.requestPasswordReset({ email: 'fulano@exemplo.com.br' });

		expect(fetchFn).toHaveBeenCalledTimes(1);
		const [url, init] = fetchFn.mock.calls[0];
		expect(url).toBe('http://localhost:3001/api/auth/forgot-password');
		expect(init?.method).toBe('POST');
		expect(init?.headers).toMatchObject({
			'Content-Type': 'application/json',
			[CORRELATION_ID_HEADER]: 'corr-123'
		});
		expect(init?.body).toBe(JSON.stringify({ email: 'fulano@exemplo.com.br' }));
		expect(result.correlationId).toBe('corr-123');
		expect(result.data.message).toContain('instruções de recuperação');
	});

	it('injects Authorization header when token provider returns a token', async () => {
		const fetchFn = vi
			.fn<typeof fetch>()
			.mockResolvedValue(jsonResponse({ message: 'Senha redefinida com sucesso.' }));

		const httpClient = createHttpClient({
			getAuthToken: () => 'jwt-token-abc',
			generateCorrelationId: () => 'corr-auth',
			fetchFn
		});
		const client = createPasswordRecoveryClient(httpClient);

		await client.confirmPasswordReset({ token: 'tok-1', nova_senha: 'Password1!' });

		const [, init] = fetchFn.mock.calls[0];
		expect(init?.headers).toMatchObject({
			Authorization: 'Bearer jwt-token-abc',
			[CORRELATION_ID_HEADER]: 'corr-auth'
		});
	});

	it('calls POST /api/auth/reset-password and maps 400 detail into ApiError', async () => {
		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			jsonResponse(
				{ detail: 'Token de recuperação inválido ou expirado.' },
				{
					status: 400,
					headers: {
						'content-type': 'application/json',
						[CORRELATION_ID_HEADER]: 'corr-err'
					}
				}
			)
		);

		const httpClient = createHttpClient({
			generateCorrelationId: () => 'corr-err',
			fetchFn
		});
		const client = createPasswordRecoveryClient(httpClient);

		await expect(
			client.confirmPasswordReset({ token: 'bad-token', nova_senha: 'Password1!' })
		).rejects.toEqual(
			expect.objectContaining<Partial<ApiError>>({
				name: 'ApiError',
				status: 400,
				message: 'Token de recuperação inválido ou expirado.',
				correlationId: 'corr-err'
			})
		);
	});

	it('validates strong passwords with the same policy as core-service', () => {
		expect(isStrongPassword('Veridt@1')).toBe(true);
		expect(isStrongPassword('weak')).toBe(false);
		expect(isStrongPassword('NoSymbol123')).toBe(false);
		expect(isStrongPassword('NoNumber@')).toBe(false);
	});

	it('formats CPF progressively as 000.000.000-00 and caps at 11 digits', () => {
		expect(formatCpf('')).toBe('');
		expect(formatCpf('123')).toBe('123');
		expect(formatCpf('1234')).toBe('123.4');
		expect(formatCpf('1234567')).toBe('123.456.7');
		expect(formatCpf('12345678909')).toBe('123.456.789-09');
		expect(formatCpf('123.456.789-09 extra 999')).toBe('123.456.789-09');
	});

	it('calls POST /api/auth/login and normalizes token and user payload', async () => {
		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			jsonResponse(
				{
					token: 'jwt-login-123',
					user: {
						id: '11111111-1111-1111-1111-111111111111',
						nome_completo: 'Dr. Fulano da Silva',
						email: 'fulano@exemplo.com.br',
						tipo_perfil: 'ADVOGADO',
						numero_oab: '45.678 / BA'
					}
				},
				{
					headers: {
						'content-type': 'application/json',
						[CORRELATION_ID_HEADER]: 'corr-login'
					}
				}
			)
		);

		const httpClient = createHttpClient({
			baseUrl: 'http://localhost:3001',
			generateCorrelationId: () => 'corr-login',
			fetchFn
		});
		const client = createAuthLoginClient(httpClient);

		const result = await client.login({
			email: 'fulano@exemplo.com.br',
			senha: 'Password1!'
		});

		const [url, init] = fetchFn.mock.calls[0];
		expect(url).toBe('http://localhost:3001/api/auth/login');
		expect(init?.method).toBe('POST');
		expect(result.correlationId).toBe('corr-login');
		expect(result.data).toEqual({
			token: 'jwt-login-123',
			user: {
				id: '11111111-1111-1111-1111-111111111111',
				nome: 'Dr. Fulano da Silva',
				email: 'fulano@exemplo.com.br',
				role: 'ADVOGADO',
				oab: '45.678 / BA'
			}
		});
	});

	it('calls POST /api/auth/register and enforces numero_oab = null for USUARIO_COMUM (Decisão D1)', async () => {
		const fetchFn = vi
			.fn<typeof fetch>()
			.mockResolvedValue(jsonResponse({ message: 'Usuário cadastrado com sucesso.' }));

		const httpClient = createHttpClient({
			baseUrl: 'http://localhost:3001',
			generateCorrelationId: () => 'corr-reg',
			fetchFn
		});
		const client = createAuthRegisterClient(httpClient);

		await client.register({
			nome_completo: 'Maria Oliveira',
			email: 'maria@exemplo.com.br',
			senha: 'Password1!',
			cpf: '123.456.789-09',
			tipo_perfil: 'USUARIO_COMUM',
			numero_oab: '99.999 / BA',
			termos_aceitos: true
		});

		const [url, init] = fetchFn.mock.calls[0];
		expect(url).toBe('http://localhost:3001/api/auth/register');
		expect(JSON.parse(String(init?.body))).toMatchObject({
			tipo_perfil: 'USUARIO_COMUM',
			numero_oab: null,
			termos_aceitos: true
		});
	});

	it('calls POST /api/auth/logout with Authorization Bearer token and X-Correlation-ID', async () => {
		const fetchFn = vi
			.fn<typeof fetch>()
			.mockResolvedValue(jsonResponse({ message: 'Logout realizado e token revogado' }));

		const httpClient = createHttpClient({
			baseUrl: 'http://localhost:3001',
			getAuthToken: () => 'jwt-active-999',
			generateCorrelationId: () => 'corr-logout',
			fetchFn
		});
		const client = createAuthLogoutClient(httpClient);

		const result = await client.logout();

		const [url, init] = fetchFn.mock.calls[0];
		expect(url).toBe('http://localhost:3001/api/auth/logout');
		expect(init?.method).toBe('POST');
		expect(init?.headers).toMatchObject({
			Authorization: 'Bearer jwt-active-999',
			[CORRELATION_ID_HEADER]: 'corr-logout'
		});
		expect(result.data.message).toBe('Logout realizado e token revogado');
	});
});
