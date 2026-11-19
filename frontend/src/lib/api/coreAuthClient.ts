import { authSession } from '../auth/session.svelte.ts';
import {
	createHttpClient,
	type ApiResponse,
	type HttpPostClient,
	type RequestOptions
} from './httpClient.ts';

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

export function isStrongPassword(password: string): boolean {
	return STRONG_PASSWORD_REGEX.test(password);
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

export const passwordRecoveryClient: PasswordRecoveryClient =
	createPasswordRecoveryClient(coreAuthHttpClient);
