export const CORRELATION_ID_HEADER = 'X-Correlation-ID';

export interface HttpClientConfig {
	baseUrl?: string;
	getAuthToken?: () => string | null;
	generateCorrelationId?: () => string;
	fetchFn?: typeof fetch;
}

export interface RequestOptions {
	correlationId?: string;
	headers?: Record<string, string>;
	signal?: AbortSignal;
}

export interface ApiResponse<T> {
	data: T;
	correlationId: string;
}

export interface HttpClient {
	post<TResponse, TBody = unknown>(
		path: string,
		body: TBody,
		options?: RequestOptions
	): Promise<ApiResponse<TResponse>>;
}

export class ApiError extends Error {
	readonly status: number;
	readonly correlationId: string;

	constructor(message: string, status: number, correlationId: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.correlationId = correlationId;
	}
}

function defaultCorrelationId(): string {
	if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
		return crypto.randomUUID();
	}
	return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function extractErrorMessage(payload: unknown, fallbackStatus: number): string {
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		if (typeof record.detail === 'string' && record.detail.trim()) {
			return record.detail;
		}
		if (Array.isArray(record.detail) && record.detail.length > 0) {
			const first = record.detail[0] as Record<string, unknown> | undefined;
			if (first && typeof first.msg === 'string') {
				return first.msg;
			}
		}
		if (typeof record.message === 'string' && record.message.trim()) {
			return record.message;
		}
	}
	return `Erro na requisição (HTTP ${fallbackStatus}).`;
}

export function createHttpClient(config: HttpClientConfig = {}): HttpClient {
	const baseUrl = (config.baseUrl ?? '').replace(/\/+$/, '');
	const generateCorrelationId = config.generateCorrelationId ?? defaultCorrelationId;
	const fetchFn = config.fetchFn ?? fetch;

	return {
		async post<TResponse, TBody = unknown>(
			path: string,
			body: TBody,
			options: RequestOptions = {}
		): Promise<ApiResponse<TResponse>> {
			const correlationId = options.correlationId ?? generateCorrelationId();
			const headers: Record<string, string> = {
				'Content-Type': 'application/json',
				[CORRELATION_ID_HEADER]: correlationId,
				...options.headers
			};

			const token = config.getAuthToken?.();
			if (token) {
				headers.Authorization = `Bearer ${token}`;
			}

			const url = `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
			const response = await fetchFn(url, {
				method: 'POST',
				headers,
				body: JSON.stringify(body),
				signal: options.signal
			});

			const responseCorrelationId = response.headers.get(CORRELATION_ID_HEADER) ?? correlationId;

			let payload: unknown = null;
			const contentType = response.headers.get('content-type') ?? '';
			if (contentType.includes('application/json')) {
				payload = await response.json();
			}

			if (!response.ok) {
				throw new ApiError(
					extractErrorMessage(payload, response.status),
					response.status,
					responseCorrelationId
				);
			}

			return {
				data: payload as TResponse,
				correlationId: responseCorrelationId
			};
		}
	};
}
