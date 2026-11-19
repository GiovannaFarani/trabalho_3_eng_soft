export type UserRole = 'ADVOGADO' | 'USUARIO_COMUM' | (string & {});

export interface AuthenticatedUser {
	id: string;
	nome: string | null;
	email: string | null;
	role: UserRole;
	oab: string | null;
}

/**
 * Interface Segregation Principle (ISP):
 * Narrow contract for HTTP clients that only need to read the active bearer token.
 */
export interface TokenProvider {
	getAuthToken(): string | null;
}

/**
 * Interface Segregation Principle (ISP):
 * Read-only session contract for UI components (e.g. header, route guards).
 */
export interface AuthSessionReader {
	readonly token: string | null;
	readonly user: AuthenticatedUser | null;
	readonly isAuthenticated: boolean;
}

/**
 * Interface Segregation Principle (ISP):
 * Write-only session contract for login, logout, and 401 invalidation handlers.
 */
export interface AuthSessionWriter {
	setSession(token: string, user?: AuthenticatedUser | null): void;
	clearSession(): void;
}

export interface AuthSessionStore extends TokenProvider, AuthSessionReader, AuthSessionWriter {}

export interface KeyValueStorage {
	getItem(key: string): string | null;
	setItem(key: string, value: string): void;
	removeItem(key: string): void;
}

export const AUTH_TOKEN_STORAGE_KEY = 'veridt.auth.token';
export const AUTH_USER_STORAGE_KEY = 'veridt.auth.user';

interface JwtPayload {
	sub?: unknown;
	nome?: unknown;
	email?: unknown;
	role?: unknown;
	oab?: unknown;
	exp?: unknown;
}

function decodeBase64Url(segment: string): string | null {
	try {
		const normalized = segment.replace(/-/g, '+').replace(/_/g, '/');
		const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');

		if (typeof atob === 'function') {
			const binary = atob(padded);
			const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
			return new TextDecoder().decode(bytes);
		}

		if (typeof Buffer !== 'undefined') {
			return Buffer.from(padded, 'base64').toString('utf-8');
		}

		return null;
	} catch {
		return null;
	}
}

export function isTokenExpired(token: string, nowMs: number = Date.now()): boolean {
	const parts = token.split('.');
	if (parts.length !== 3) return false;

	const decoded = decodeBase64Url(parts[1]);
	if (!decoded) return false;

	try {
		const payload = JSON.parse(decoded) as JwtPayload;
		if (typeof payload.exp === 'number') {
			return payload.exp * 1000 <= nowMs;
		}
		return false;
	} catch {
		return false;
	}
}

export function decodeJwtUser(token: string, nowMs: number = Date.now()): AuthenticatedUser | null {
	const parts = token.split('.');
	if (parts.length !== 3) return null;

	const decoded = decodeBase64Url(parts[1]);
	if (!decoded) return null;

	try {
		const payload = JSON.parse(decoded) as JwtPayload;
		if (typeof payload.exp === 'number' && payload.exp * 1000 <= nowMs) {
			return null;
		}
		if (typeof payload.sub !== 'string' || !payload.sub.trim()) {
			return null;
		}
		if (typeof payload.role !== 'string' || !payload.role.trim()) {
			return null;
		}

		return {
			id: payload.sub,
			nome: typeof payload.nome === 'string' && payload.nome.trim() ? payload.nome.trim() : null,
			email:
				typeof payload.email === 'string' && payload.email.trim() ? payload.email.trim() : null,
			role: payload.role,
			oab: typeof payload.oab === 'string' && payload.oab.trim() ? payload.oab.trim() : null
		};
	} catch {
		return null;
	}
}

const IGNORED_NAME_PREFIXES = ['dr.', 'dra.', 'dr', 'dra', 'sr.', 'sra.'];

export function formatUserInitials(name: string | null | undefined, email?: string | null): string {
	const source = (name ?? '').trim();
	if (source) {
		const words = source
			.split(/\s+/)
			.filter((word) => word && !IGNORED_NAME_PREFIXES.includes(word.toLowerCase()));
		const usable = words.length > 0 ? words : source.split(/\s+/).filter(Boolean);
		if (usable.length === 1) {
			return usable[0].slice(0, 2).toUpperCase();
		}
		return `${usable[0][0]}${usable[usable.length - 1][0]}`.toUpperCase();
	}

	const fallbackEmail = (email ?? '').trim();
	if (fallbackEmail) {
		return fallbackEmail.slice(0, 2).toUpperCase();
	}

	return 'US';
}

export function formatUserDisplayLabel(user: AuthenticatedUser | null): string {
	if (!user) return 'Usuário';
	const name = user.nome || user.email || 'Usuário';
	if (user.role === 'ADVOGADO' && user.oab) {
		return `${name} - OAB ${user.oab}`;
	}
	return name;
}

function getBrowserStorage(): KeyValueStorage | null {
	if (typeof window === 'undefined') return null;
	try {
		return window.localStorage;
	} catch {
		return null;
	}
}

function readStoredUser(storage: KeyValueStorage | null): AuthenticatedUser | null {
	if (!storage) return null;
	const raw = storage.getItem(AUTH_USER_STORAGE_KEY);
	if (!raw) return null;
	try {
		const parsed = JSON.parse(raw) as Partial<AuthenticatedUser>;
		if (typeof parsed.id === 'string' && typeof parsed.role === 'string') {
			return {
				id: parsed.id,
				nome: typeof parsed.nome === 'string' ? parsed.nome : null,
				email: typeof parsed.email === 'string' ? parsed.email : null,
				role: parsed.role,
				oab: typeof parsed.oab === 'string' ? parsed.oab : null
			};
		}
		return null;
	} catch {
		return null;
	}
}

export interface AuthSessionStoreConfig {
	storage?: KeyValueStorage | null;
	now?: () => number;
}

export function createAuthSessionStore(config: AuthSessionStoreConfig = {}): AuthSessionStore {
	const storage = config.storage !== undefined ? config.storage : getBrowserStorage();
	const now = config.now ?? (() => Date.now());

	let initialToken: string | null = null;
	let initialUser: AuthenticatedUser | null = null;

	const storedToken = storage?.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim() ?? null;
	if (storedToken) {
		if (isTokenExpired(storedToken, now())) {
			storage?.removeItem(AUTH_TOKEN_STORAGE_KEY);
			storage?.removeItem(AUTH_USER_STORAGE_KEY);
		} else {
			initialToken = storedToken;
			initialUser = readStoredUser(storage) ?? decodeJwtUser(storedToken, now());
		}
	}

	let token = $state<string | null>(initialToken);
	let user = $state<AuthenticatedUser | null>(initialUser);

	return {
		get token() {
			return token;
		},
		get user() {
			return user;
		},
		get isAuthenticated() {
			return token !== null;
		},
		getAuthToken() {
			if (token && isTokenExpired(token, now())) {
				token = null;
				user = null;
				storage?.removeItem(AUTH_TOKEN_STORAGE_KEY);
				storage?.removeItem(AUTH_USER_STORAGE_KEY);
				return null;
			}
			return token;
		},
		setSession(nextToken: string, nextUser?: AuthenticatedUser | null) {
			const trimmed = nextToken.trim();
			if (!trimmed || isTokenExpired(trimmed, now())) {
				this.clearSession();
				return;
			}

			const resolvedUser = nextUser ?? decodeJwtUser(trimmed, now());
			token = trimmed;
			user = resolvedUser;

			storage?.setItem(AUTH_TOKEN_STORAGE_KEY, trimmed);
			if (resolvedUser) {
				storage?.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(resolvedUser));
			} else {
				storage?.removeItem(AUTH_USER_STORAGE_KEY);
			}
		},
		clearSession() {
			token = null;
			user = null;
			storage?.removeItem(AUTH_TOKEN_STORAGE_KEY);
			storage?.removeItem(AUTH_USER_STORAGE_KEY);
		}
	};
}

export const authSession: AuthSessionStore = createAuthSessionStore();
