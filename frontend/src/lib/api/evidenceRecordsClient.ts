import { authSession } from '../auth/session.svelte.ts';
import {
	createHttpClient,
	type ApiResponse,
	type HttpGetClient,
	type RequestOptions
} from './httpClient.ts';

export type BackendRecordStatus = 'INICIADO' | 'PROCESSANDO' | 'CONCLUIDO' | 'FALHA';

export type EvidenceRecordStatus =
	'INICIADO' | 'PROCESSANDO' | 'CONCLUIDO' | 'FALHA - Crédito Estornado';

export interface EvidenceRecordDto {
	id: string;
	titulo: string;
	url_alvo: string;
	data_hora_inicio: string;
	data_hora_fim: string | null;
	detalhes_resumo: string;
	status: BackendRecordStatus;
}

export interface EvidenceRecord {
	id: string;
	title: string;
	url: string;
	startDate: string;
	startTime: string;
	endDate: string | null;
	endTime: string | null;
	detailsSummary: string;
	detailsMeta: string;
	status: EvidenceRecordStatus;
}

/**
 * Interface Segregation Principle (ISP):
 * Segregated read-only client contract exposing only record listing
 * available in evidence-service (`GET /api/records/`).
 * Components that list records depend solely on this narrow interface.
 */
export interface RecordsReaderClient {
	listRecords(options?: RequestOptions): Promise<ApiResponse<EvidenceRecord[]>>;
}

const NAIVE_ISO_TIMESTAMP_REGEX = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})/;

const brasiliaDateFormatter = new Intl.DateTimeFormat('pt-BR', {
	timeZone: 'America/Sao_Paulo',
	day: '2-digit',
	month: '2-digit',
	year: 'numeric'
});

const brasiliaTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
	timeZone: 'America/Sao_Paulo',
	hour: '2-digit',
	minute: '2-digit',
	second: '2-digit',
	hour12: false
});

export function mapRecordStatus(status: BackendRecordStatus): EvidenceRecordStatus {
	if (status === 'FALHA') {
		return 'FALHA - Crédito Estornado';
	}
	return status;
}

export function formatRecordTimestamp(value: string | null | undefined): {
	date: string | null;
	time: string | null;
} {
	if (!value) {
		return { date: null, time: null };
	}

	const trimmed = value.trim();
	const hasTimezone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(trimmed);

	if (!hasTimezone) {
		const match = NAIVE_ISO_TIMESTAMP_REGEX.exec(trimmed);
		if (match) {
			const [, year, month, day, hour, minute, second] = match;
			return {
				date: `${day}/${month}/${year}`,
				time: `${hour}:${minute}:${second}`
			};
		}
	}

	const parsed = new Date(trimmed);
	if (Number.isNaN(parsed.getTime())) {
		return { date: null, time: null };
	}

	return {
		date: brasiliaDateFormatter.format(parsed),
		time: brasiliaTimeFormatter.format(parsed)
	};
}

export function splitDetailsSummary(summary: string): {
	detailsSummary: string;
	detailsMeta: string;
} {
	const parts = summary
		.split('•')
		.map((part) => part.trim())
		.filter(Boolean);

	if (parts.length <= 1) {
		return { detailsSummary: summary.trim(), detailsMeta: '' };
	}

	if (parts.length >= 4) {
		return {
			detailsSummary: parts.slice(0, 2).join(' • '),
			detailsMeta: parts.slice(2).join(' • ')
		};
	}

	return {
		detailsSummary: parts[0],
		detailsMeta: parts.slice(1).join(' • ')
	};
}

export function mapEvidenceRecordDto(dto: EvidenceRecordDto): EvidenceRecord {
	const start = formatRecordTimestamp(dto.data_hora_inicio);
	const end = formatRecordTimestamp(dto.data_hora_fim);
	const details = splitDetailsSummary(dto.detalhes_resumo);

	return {
		id: dto.id,
		title: dto.titulo,
		url: dto.url_alvo,
		startDate: start.date ?? '—',
		startTime: start.time ?? '—',
		endDate: end.date,
		endTime: end.time,
		detailsSummary: details.detailsSummary,
		detailsMeta: details.detailsMeta,
		status: mapRecordStatus(dto.status)
	};
}

export function createRecordsReaderClient(httpClient: HttpGetClient): RecordsReaderClient {
	return {
		async listRecords(options) {
			const response = await httpClient.get<EvidenceRecordDto[]>('/api/records/', options);
			const items = Array.isArray(response.data) ? response.data : [];
			return {
				data: items.map(mapEvidenceRecordDto),
				correlationId: response.correlationId
			};
		}
	};
}

const evidenceServiceBaseUrl =
	(import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env
		?.VITE_EVIDENCE_SERVICE_URL ?? '';

export const evidenceHttpClient = createHttpClient({
	baseUrl: evidenceServiceBaseUrl,
	getAuthToken: () => authSession.getAuthToken(),
	onUnauthorized: () => authSession.clearSession()
});

export const recordsReaderClient: RecordsReaderClient =
	createRecordsReaderClient(evidenceHttpClient);
