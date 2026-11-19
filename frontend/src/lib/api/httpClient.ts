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

/**
 * Interface Segregation Principle (ISP):
 * Segregated read-only HTTP transport contract for clients that only perform GET requests.
 */
export interface HttpGetClient {
	get<TResponse>(path: string, options?: RequestOptions): Promise<ApiResponse<TResponse>>;
}

/**
 * Interface Segregation Principle (ISP):
 * Segregated write HTTP transport contract for clients that only perform POST requests.
 */
export interface HttpPostClient {
	post<TResponse, TBody = unknown>(
		path: string,
		body: TBody,
		options?: RequestOptions
	): Promise<ApiResponse<TResponse>>;
}

export interface HttpClient extends HttpGetClient, HttpPostClient {}

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

	async function request<TResponse>(
		method: 'GET' | 'POST',
		path: string,
		options: RequestOptions = {},
		body?: unknown
	): Promise<ApiResponse<TResponse>> {
		const correlationId = options.correlationId ?? generateCorrelationId();
		const headers: Record<string, string> = {
			[CORRELATION_ID_HEADER]: correlationId,
			...options.headers
		};

		if (body !== undefined) {
			headers['Content-Type'] = headers['Content-Type'] ?? 'application/json';
		}

		const token = config.getAuthToken?.();
		if (token) {
			headers.Authorization = `Bearer ${token}`;
		}

		const url = `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
		const response = await fetchFn(url, {
			method,
			headers,
			body: body !== undefined ? JSON.stringify(body) : undefined,
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

	return {
		get<TResponse>(path: string, options: RequestOptions = {}): Promise<ApiResponse<TResponse>> {
			return request<TResponse>('GET', path, options);
		},
		post<TResponse, TBody = unknown>(
			path: string,
			body: TBody,
			options: RequestOptions = {}
		): Promise<ApiResponse<TResponse>> {
			return request<TResponse>('POST', path, options, body);
		}
	};
}
