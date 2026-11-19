import { authSession, type AuthenticatedUser, type UserRole } from '../auth/session.svelte.ts';
import {
	createHttpClient,
	type ApiResponse,
	type HttpPostClient,
	type RequestOptions
} from './httpClient.ts';

export type ProfileTypeDto = 'ADVOGADO' | 'USUARIO_COMUM';

export interface LoginRequest {
	email: string;
	senha: string;
}

export interface BackendUserDto {
	id?: string;
	sub?: string;
	nome?: string | null;
	nome_completo?: string | null;
	email?: string | null;
	role?: UserRole;
	tipo_perfil?: UserRole;
	oab?: string | null;
	numero_oab?: string | null;
}

export interface LoginResponseDto {
	token?: string;
	access_token?: string;
	user?: BackendUserDto | null;
}

export interface LoginResult {
	token: string;
	user: AuthenticatedUser | null;
}

export interface RegisterRequest {
	nome_completo: string;
	email: string;
	senha: string;
	cpf: string;
	tipo_perfil: ProfileTypeDto;
	numero_oab: string | null;
	termos_aceitos: boolean;
}

export interface RegisterResponse {
	message?: string;
	token?: string;
	access_token?: string;
	user?: BackendUserDto | null;
}

export interface ForgotPasswordRequest {
	email: string;
}

export interface ResetPasswordRequest {
	token: string;
	nova_senha: string;
}

export interface MessageResponse {
	message: string;
}

/**
 * Interface Segregation Principle (ISP):
 * Narrow contract for authenticating a user (`POST /api/auth/login`).
 */
export interface AuthLoginClient {
	login(payload: LoginRequest, options?: RequestOptions): Promise<ApiResponse<LoginResult>>;
}

/**
 * Interface Segregation Principle (ISP):
 * Narrow contract for registering a new user (`POST /api/auth/register`).
 */
export interface AuthRegisterClient {
	register(
		payload: RegisterRequest,
		options?: RequestOptions
	): Promise<ApiResponse<RegisterResponse>>;
}

/**
 * Interface Segregation Principle (ISP):
 * Narrow contract for revoking the active session (`POST /api/auth/logout`).
 * Workspace components depend only on this interface, never on login/register/recovery.
 */
export interface AuthLogoutClient {
	logout(options?: RequestOptions): Promise<ApiResponse<MessageResponse>>;
}

/**
 * Interface Segregation Principle (ISP):
 * Segregated client contract exposing only password recovery operations
 * available in core-service (`/api/auth/forgot-password` and `/api/auth/reset-password`).
 * Components handling password recovery depend only on this narrow interface.
 */
export interface PasswordRecoveryClient {
	requestPasswordReset(
		payload: ForgotPasswordRequest,
		options?: RequestOptions
	): Promise<ApiResponse<MessageResponse>>;
	confirmPasswordReset(
		payload: ResetPasswordRequest,
		options?: RequestOptions
	): Promise<ApiResponse<MessageResponse>>;
}

export const STRONG_PASSWORD_REGEX =
	/^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;

export const PASSWORD_RULE_MESSAGE =
	'A senha deve ter no mínimo 8 caracteres, com letras, números e símbolos (@$!%*#?&).';

export const TERMS_REQUIRED_MESSAGE =
	'É obrigatório aceitar os Termos de Uso e Política de Privacidade.';

export function isStrongPassword(password: string): boolean {
	return STRONG_PASSWORD_REGEX.test(password);
}

export function formatCpf(value: string): string {
	const digits = value.replace(/\D/g, '').slice(0, 11);
	if (digits.length <= 3) return digits;
	if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
	if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
	return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

export function normalizeBackendUser(
	dto: BackendUserDto | null | undefined
): AuthenticatedUser | null {
	if (!dto) return null;
	const id = dto.id ?? dto.sub;
	const role = dto.role ?? dto.tipo_perfil;
	if (!id || !role) return null;

	return {
		id: String(id),
		nome: (dto.nome ?? dto.nome_completo ?? null)?.trim() || null,
		email: dto.email?.trim() || null,
		role,
		oab: (dto.oab ?? dto.numero_oab ?? null)?.trim() || null
	};
}

export function createAuthLoginClient(httpClient: HttpPostClient): AuthLoginClient {
	return {
		async login(payload, options) {
			const response = await httpClient.post<LoginResponseDto, LoginRequest>(
				'/api/auth/login',
				payload,
				options
			);
			const token = response.data?.token ?? response.data?.access_token ?? '';
			if (!token) {
				throw new Error('Resposta de autenticação inválida: token ausente.');
			}
			return {
				data: {
					token,
					user: normalizeBackendUser(response.data?.user)
				},
				correlationId: response.correlationId
			};
		}
	};
}

export function createAuthRegisterClient(httpClient: HttpPostClient): AuthRegisterClient {
	return {
		register(payload, options) {
			const normalizedPayload: RegisterRequest = {
				...payload,
				numero_oab: payload.tipo_perfil === 'ADVOGADO' ? payload.numero_oab : null
			};
			return httpClient.post<RegisterResponse, RegisterRequest>(
				'/api/auth/register',
				normalizedPayload,
				options
			);
		}
	};
}

export function createAuthLogoutClient(httpClient: HttpPostClient): AuthLogoutClient {
	return {
		logout(options) {
			return httpClient.post<MessageResponse, Record<string, never>>(
				'/api/auth/logout',
				{},
				options
			);
		}
	};
}

export function createPasswordRecoveryClient(httpClient: HttpPostClient): PasswordRecoveryClient {
	return {
		requestPasswordReset(payload, options) {
			return httpClient.post<MessageResponse, ForgotPasswordRequest>(
				'/api/auth/forgot-password',
				payload,
				options
			);
		},
		confirmPasswordReset(payload, options) {
			return httpClient.post<MessageResponse, ResetPasswordRequest>(
				'/api/auth/reset-password',
				payload,
				options
			);
		}
	};
}

const coreServiceBaseUrl =
	(import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env
		?.VITE_CORE_SERVICE_URL ?? '';

export const coreAuthHttpClient = createHttpClient({
	baseUrl: coreServiceBaseUrl,
	getAuthToken: () => authSession.getAuthToken(),
	onUnauthorized: () => authSession.clearSession()
});

export const authLoginClient: AuthLoginClient = createAuthLoginClient(coreAuthHttpClient);

export const authRegisterClient: AuthRegisterClient = createAuthRegisterClient(coreAuthHttpClient);

export const authLogoutClient: AuthLogoutClient = createAuthLogoutClient(coreAuthHttpClient);

export const passwordRecoveryClient: PasswordRecoveryClient =
	createPasswordRecoveryClient(coreAuthHttpClient);
