import { describe, expect, it, vi } from 'vitest';
import { createPasswordRecoveryClient, isStrongPassword } from './coreAuthClient.ts';
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
});
