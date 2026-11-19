import { describe, expect, it, vi } from 'vitest';
import {
	createRecordsReaderClient,
	formatRecordTimestamp,
	splitDetailsSummary,
	type EvidenceRecordDto
} from './evidenceRecordsClient.ts';
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

describe('HttpGetClient & RecordsReaderClient (ISP)', () => {
	it('calls GET /api/records/ with X-Correlation-ID and Bearer token without Content-Type', async () => {
		const backendPayload: EvidenceRecordDto[] = [
			{
				id: 'VRD-2026-0104',
				titulo: 'Oferta anunciada • Notebook Aurora 14',
				url_alvo: 'https://loja.orbita.example/notebook-aurora-14',
				data_hora_inicio: '2026-10-22T09:32:10',
				data_hora_fim: '2026-10-22T09:35:24',
				detalhes_resumo: '1 vídeo • 4 imagens • 00:03:14 • 48.5 MB',
				status: 'CONCLUIDO'
			},
			{
				id: 'VRD-2026-0101',
				titulo: 'Anúncio • Imóvel residencial',
				url_alvo: 'https://imoveis.exemplo.com.br',
				data_hora_inicio: '2026-10-21T15:42:11',
				data_hora_fim: null,
				detalhes_resumo: 'URL indisponível • 1 crédito devolvido',
				status: 'FALHA'
			}
		];

		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			jsonResponse(backendPayload, {
				headers: {
					'content-type': 'application/json',
					[CORRELATION_ID_HEADER]: 'corr-rec-1'
				}
			})
		);

		const httpClient = createHttpClient({
			baseUrl: 'http://localhost:3002',
			getAuthToken: () => 'jwt-token-xyz',
			generateCorrelationId: () => 'corr-rec-1',
			fetchFn
		});
		const client = createRecordsReaderClient(httpClient);

		const result = await client.listRecords();

		expect(fetchFn).toHaveBeenCalledTimes(1);
		const [url, init] = fetchFn.mock.calls[0];
		expect(url).toBe('http://localhost:3002/api/records/');
		expect(init?.method).toBe('GET');
		expect(init?.body).toBeUndefined();
		expect(init?.headers).toMatchObject({
			Authorization: 'Bearer jwt-token-xyz',
			[CORRELATION_ID_HEADER]: 'corr-rec-1'
		});
		expect((init?.headers as Record<string, string>)['Content-Type']).toBeUndefined();

		expect(result.correlationId).toBe('corr-rec-1');
		expect(result.data).toEqual([
			{
				id: 'VRD-2026-0104',
				title: 'Oferta anunciada • Notebook Aurora 14',
				url: 'https://loja.orbita.example/notebook-aurora-14',
				startDate: '22/10/2026',
				startTime: '09:32:10',
				endDate: '22/10/2026',
				endTime: '09:35:24',
				detailsSummary: '1 vídeo • 4 imagens',
				detailsMeta: '00:03:14 • 48.5 MB',
				status: 'CONCLUIDO'
			},
			{
				id: 'VRD-2026-0101',
				title: 'Anúncio • Imóvel residencial',
				url: 'https://imoveis.exemplo.com.br',
				startDate: '21/10/2026',
				startTime: '15:42:11',
				endDate: null,
				endTime: null,
				detailsSummary: 'URL indisponível',
				detailsMeta: '1 crédito devolvido',
				status: 'FALHA - Crédito Estornado'
			}
		]);
	});

	it('maps 401 unauthorized response into ApiError', async () => {
		const fetchFn = vi.fn<typeof fetch>().mockResolvedValue(
			jsonResponse(
				{ detail: 'Autenticação necessária.' },
				{
					status: 401,
					headers: {
						'content-type': 'application/json',
						[CORRELATION_ID_HEADER]: 'corr-401'
					}
				}
			)
		);

		const httpClient = createHttpClient({
			generateCorrelationId: () => 'corr-401',
			fetchFn
		});
		const client = createRecordsReaderClient(httpClient);

		await expect(client.listRecords()).rejects.toEqual(
			expect.objectContaining<Partial<ApiError>>({
				name: 'ApiError',
				status: 401,
				message: 'Autenticação necessária.',
				correlationId: 'corr-401'
			})
		);
	});

	it('formats UTC timestamps to Brasilia time (UTC-03:00) and handles naive timestamps', () => {
		expect(formatRecordTimestamp('2026-10-22T13:14:00Z')).toEqual({
			date: '22/10/2026',
			time: '10:14:00'
		});
		expect(formatRecordTimestamp('2026-10-22T10:14:00')).toEqual({
			date: '22/10/2026',
			time: '10:14:00'
		});
		expect(formatRecordTimestamp(null)).toEqual({ date: null, time: null });
	});

	it('splits detalhes_resumo into primary summary and secondary metadata', () => {
		expect(splitDetailsSummary('1 vídeo em gravação • 1 imagem • sessão ativa')).toEqual({
			detailsSummary: '1 vídeo em gravação',
			detailsMeta: '1 imagem • sessão ativa'
		});
		expect(splitDetailsSummary('Sem detalhes extras')).toEqual({
			detailsSummary: 'Sem detalhes extras',
			detailsMeta: ''
		});
	});
});
