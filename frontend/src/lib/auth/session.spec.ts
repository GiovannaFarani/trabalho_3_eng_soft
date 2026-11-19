import { describe, expect, it, vi } from 'vitest';
import { createHttpClient } from '../api/httpClient.ts';
import {
	AUTH_TOKEN_STORAGE_KEY,
	AUTH_USER_STORAGE_KEY,
	createAuthSessionStore,
	decodeJwtUser,
	formatUserDisplayLabel,
	formatUserInitials,
	type KeyValueStorage
} from './session.svelte.ts';

function createMemoryStorage(initial: Record<string, string> = {}): KeyValueStorage {
	const store = new Map<string, string>(Object.entries(initial));
	return {
		getItem: (key) => store.get(key) ?? null,
		setItem: (key, value) => {
			store.set(key, value);
		},
		removeItem: (key) => {
			store.delete(key);
		}
	};
}

function makeJwt(payload: Record<string, unknown>): string {
	const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
	const body = Buffer.from(JSON.stringify(payload), 'utf-8').toString('base64url');
	return `${header}.${body}.signature`;
}

describe('AuthSessionStore (ISP) & JWT helpers', () => {
	it('decodes UTF-8 user claims from a valid JWT', () => {
		const token = makeJwt({
			sub: '11111111-1111-1111-1111-111111111111',
			nome: 'Dr. João da Silva',
			email: 'joao@exemplo.com.br',
			role: 'ADVOGADO',
			oab: '45.678 / BA',
			exp: 2_000_000_000
		});

		expect(decodeJwtUser(token, 1_700_000_000_000)).toEqual({
			id: '11111111-1111-1111-1111-111111111111',
			nome: 'Dr. João da Silva',
			email: 'joao@exemplo.com.br',
			role: 'ADVOGADO',
			oab: '45.678 / BA'
		});
	});

	it('returns null for expired JWTs', () => {
		const expiredToken = makeJwt({
			sub: 'user-1',
			role: 'USUARIO_COMUM',
			exp: 1_000
		});

		expect(decodeJwtUser(expiredToken, 2_000_000)).toBeNull();
	});

	it('persists, hydrates, and clears session state via storage', () => {
		const nowMs = 1_700_000_000_000;
		const storage = createMemoryStorage();
		const token = makeJwt({
			sub: 'user-42',
			nome: 'Maria Oliveira',
			email: 'maria@exemplo.com.br',
			role: 'USUARIO_COMUM',
			exp: Math.floor(nowMs / 1000) + 3600
		});

		const session = createAuthSessionStore({ storage, now: () => nowMs });
		expect(session.isAuthenticated).toBe(false);

		session.setSession(token);
		expect(session.isAuthenticated).toBe(true);
		expect(session.getAuthToken()).toBe(token);
		expect(session.user?.nome).toBe('Maria Oliveira');
		expect(storage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBe(token);

		const rehydrated = createAuthSessionStore({ storage, now: () => nowMs });
		expect(rehydrated.isAuthenticated).toBe(true);
		expect(rehydrated.user?.id).toBe('user-42');

		rehydrated.clearSession();
		expect(rehydrated.isAuthenticated).toBe(false);
		expect(rehydrated.user).toBeNull();
		expect(storage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();
		expect(storage.getItem(AUTH_USER_STORAGE_KEY)).toBeNull();
	});

	it('auto-clears expired tokens on hydration and onUnauthorized 401 responses', async () => {
		const nowMs = 1_700_000_000_000;
		const expiredToken = makeJwt({
			sub: 'user-1',
			role: 'ADVOGADO',
			exp: Math.floor(nowMs / 1000) - 10
		});
		const expiredStorage = createMemoryStorage({ [AUTH_TOKEN_STORAGE_KEY]: expiredToken });

		const hydrated = createAuthSessionStore({ storage: expiredStorage, now: () => nowMs });
		expect(hydrated.isAuthenticated).toBe(false);
		expect(expiredStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();

		const activeStorage = createMemoryStorage();
		const validToken = makeJwt({
			sub: 'user-2',
			role: 'ADVOGADO',
			exp: Math.floor(nowMs / 1000) + 3600
		});
		const activeSession = createAuthSessionStore({ storage: activeStorage, now: () => nowMs });
		activeSession.setSession(validToken);

		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			new Response(JSON.stringify({ detail: 'Sessão encerrada. Faça login novamente' }), {
				status: 401,
				headers: { 'content-type': 'application/json' }
			})
		);

		const httpClient = createHttpClient({
			getAuthToken: () => activeSession.getAuthToken(),
			onUnauthorized: () => activeSession.clearSession(),
			fetchFn
		});

		await expect(httpClient.get('/api/records/')).rejects.toThrow('Sessão encerrada');
		expect(activeSession.isAuthenticated).toBe(false);
	});

	it('formats user initials and display labels for ADVOGADO and USUARIO_COMUM', () => {
		expect(formatUserInitials('Dr. Fulano da Silva')).toBe('FS');
		expect(formatUserInitials(null, 'ana@exemplo.com.br')).toBe('AN');

		expect(
			formatUserDisplayLabel({
				id: '1',
				nome: 'Dr. Fulano da Silva',
				email: 'fulano@exemplo.com.br',
				role: 'ADVOGADO',
				oab: '45.678 / BA'
			})
		).toBe('Dr. Fulano da Silva - OAB 45.678 / BA');

		expect(
			formatUserDisplayLabel({
				id: '2',
				nome: 'Maria Oliveira',
				email: 'maria@exemplo.com.br',
				role: 'USUARIO_COMUM',
				oab: null
			})
		).toBe('Maria Oliveira');
	});
});
