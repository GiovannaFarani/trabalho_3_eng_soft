<script lang="ts">
	import {
		ArrowUpRight,
		CalendarDays,
		ChevronDown,
		CircleAlert,
		CirclePlay,
		FileCheckCorner,
		Info,
		LoaderCircle,
		Plus,
		RefreshCw,
		Search,
		SlidersHorizontal
	} from '@lucide/svelte';
	import { Button, TextInput } from '#lib';

	interface EvidenceRecord {
		id: string;
		title: string;
		url: string;
		startDate: string;
		startTime: string;
		endDate: string | null;
		endTime: string | null;
		detailsSummary: string;
		detailsMeta: string;
		status: 'INICIADO' | 'PROCESSANDO' | 'CONCLUIDO' | 'FALHA - Crédito Estornado';
		isActive?: boolean;
	}

	let searchQuery = $state('');

	const metrics = [
		{
			title: 'Registros concluídos',
			value: '03',
			description: 'Prontos para consulta',
			icon: FileCheckCorner,
			iconClass: 'text-status-success'
		},
		{
			title: 'Em processamento',
			value: '01',
			description: 'Preparando as evidências',
			icon: LoaderCircle,
			iconClass: 'text-status-processing'
		},
		{
			title: 'Sessões iniciadas',
			value: '01',
			description: 'Gravação em andamento',
			icon: CirclePlay,
			iconClass: 'text-status-warning'
		},
		{
			title: 'Falhas com estorno',
			value: '01',
			description: 'Crédito devolvido ao saldo',
			icon: CircleAlert,
			iconClass: 'text-status-danger'
		}
	] as const;

	const records: EvidenceRecord[] = [
		{
			id: 'VRD-2026-0105',
			title: 'Oferta anunciada • Notebook Aurora 14',
			url: 'loja.orbita.example',
			startDate: '22/10/2026',
			startTime: '10:14:00',
			endDate: null,
			endTime: null,
			detailsSummary: '1 vídeo em gravação',
			detailsMeta: '1 imagem • sessão ativa',
			status: 'INICIADO'
		},
		{
			id: 'VRD-2026-0104',
			title: 'Oferta anunciada • Notebook Aurora 14',
			url: 'loja.orbita.example',
			startDate: '22/10/2026',
			startTime: '09:32:10',
			endDate: '22/10/2026',
			endTime: '09:35:24',
			detailsSummary: '1 vídeo • 4 imagens',
			detailsMeta: '00:03:14 • 48.5 MB',
			status: 'CONCLUIDO',
			isActive: true
		},
		{
			id: 'VRD-2026-0103',
			title: 'Publicação • Perfil Comercial',
			url: 'rede.exemplo.com.br',
			startDate: '22/10/2026',
			startTime: '09:20:00',
			endDate: null,
			endTime: null,
			detailsSummary: 'Gerando pacote ZIP',
			detailsMeta: 'Verificação em andamento',
			status: 'PROCESSANDO'
		},
		{
			id: 'VRD-2026-0102',
			title: 'Condições de contratação',
			url: 'servicos.exemplo.com.br',
			startDate: '21/10/2026',
			startTime: '16:08:03',
			endDate: '21/10/2026',
			endTime: '16:09:50',
			detailsSummary: '1 vídeo • 2 imagens',
			detailsMeta: '00:01:47 • 22.8 MB',
			status: 'CONCLUIDO'
		},
		{
			id: 'VRD-2026-0101',
			title: 'Anúncio • Imóvel residencial',
			url: 'imoveis.exemplo.com.br',
			startDate: '21/10/2026',
			startTime: '15:42:11',
			endDate: null,
			endTime: null,
			detailsSummary: 'URL indisponível',
			detailsMeta: '1 crédito devolvido',
			status: 'FALHA - Crédito Estornado'
		},
		{
			id: 'VRD-2026-0100',
			title: 'Página de atendimento',
			url: 'ajuda.exemplo.com.br',
			startDate: '20/10/2026',
			startTime: '11:25:30',
			endDate: '20/10/2026',
			endTime: '11:27:02',
			detailsSummary: '1 vídeo • 3 imagens',
			detailsMeta: '00:01:32 • 18.4 MB',
			status: 'CONCLUIDO'
		}
	];

	const statusStyles: Record<EvidenceRecord['status'], { bg: string; text: string }> = {
		INICIADO: {
			bg: 'bg-amber-50',
			text: 'text-status-warning'
		},
		PROCESSANDO: {
			bg: 'bg-status-processing-bg',
			text: 'text-status-processing'
		},
		CONCLUIDO: {
			bg: 'bg-emerald-50',
			text: 'text-status-success'
		},
		'FALHA - Crédito Estornado': {
			bg: 'bg-red-50',
			text: 'text-status-danger'
		}
	};

	const filteredRecords = $derived(
		records.filter((record) => {
			if (!searchQuery.trim()) return true;
			const query = searchQuery.toLowerCase();
			return (
				record.id.toLowerCase().includes(query) ||
				record.title.toLowerCase().includes(query) ||
				record.url.toLowerCase().includes(query)
			);
		})
	);
</script>

<div class="flex flex-col gap-7">
	<div class="flex flex-row items-center justify-between gap-6">
		<div class="flex flex-col gap-2.25">
			<p class="text-xs text-on-white-tertiary">Área de trabalho / Meus Registros</p>
			<h1 class="text-[28px]! leading-tight! font-bold! text-on-white-main">
				Registros Realizados
			</h1>
			<p class="text-sm leading-[150%] text-on-white-secondary">
				Consulte suas capturas, acompanhe o processamento e acesse a cadeia de custódia de cada
				registro.
			</p>
		</div>

		<Button type="button" class="shrink-0">
			<Plus class="size-4" />
			Novo Registro
		</Button>
	</div>

	<section
		class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
		aria-label="Visão geral dos registros"
	>
		{#each metrics as metric (metric.title)}
			{@const Icon = metric.icon}
			<div
				class="flex flex-row items-start justify-between gap-4.5 rounded-xl border border-card-border bg-white p-5"
			>
				<div class="flex flex-1 flex-col gap-2.25">
					<p class="text-xs text-on-white-secondary">{metric.title}</p>
					<p class="text-[30px] leading-tight font-normal text-on-white-main">{metric.value}</p>
					<p class="text-[10px] text-on-white-tertiary">{metric.description}</p>
				</div>
				<Icon class="size-5.25 shrink-0 {metric.iconClass}" />
			</div>
		{/each}
	</section>

	<section
		class="flex flex-col overflow-hidden rounded-xl border border-card-border bg-white"
		aria-label="Registros"
	>
		<div class="flex flex-row items-center justify-between px-5 pt-5.5 pb-4.5">
			<div class="flex flex-row items-center gap-2.5">
				<h2 class="text-base! font-normal! text-on-white-main">Todos os registros</h2>
				<span
					class="rounded-md bg-surface-subtle px-2.5 py-1.5 text-[11px] text-on-white-secondary"
				>
					{filteredRecords.length} registros
				</span>
			</div>

			<div class="flex flex-row items-center gap-1.75 text-[11px] text-on-white-tertiary">
				<RefreshCw class="size-3.5" />
				<span>Atualizado às 10:16:14</span>
			</div>
		</div>

		<div class="flex flex-row flex-wrap items-center gap-3 px-5 pb-5">
			<TextInput
				type="search"
				placeholder="Buscar por título, URL ou ID do registro"
				bind:value={searchQuery}
				wrapperClass="flex-1 min-w-[260px]"
				class="h-11.5!"
			>
				{#snippet leading()}
					<Search class="size-4" />
				{/snippet}
			</TextInput>

			<Button type="button" variant="outline">
				<ChevronDown class="size-4" />
				<span>Status: Todos</span>
			</Button>

			<Button type="button" variant="outline">
				<CalendarDays class="size-4" />
				<span>20/10/2026 – 22/10/2026</span>
			</Button>

			<Button type="button" variant="outline">
				<SlidersHorizontal class="size-4" />
				<span>Filtrar</span>
			</Button>
		</div>

		<div class="overflow-x-auto">
			<div class="min-w-250">
				<div
					class="flex flex-row items-center gap-3 border-y border-card-border bg-surface-subtle px-4 py-4 text-xs font-normal text-on-white-secondary"
				>
					<span class="w-34 shrink-0">ID do Registro</span>
					<span class="min-w-50 flex-1 font-semibold">Título</span>
					<span class="w-32 shrink-0">Data/Hora Início</span>
					<span class="w-32 shrink-0">Data/Hora Fim</span>
					<span class="w-41 shrink-0">Detalhes (resumo)</span>
					<span class="w-47.5 shrink-0">Status</span>
					<span class="w-37.5 shrink-0">Ações</span>
				</div>

				{#each filteredRecords as record (record.id)}
					{@const style = statusStyles[record.status]}
					<div
						class="flex flex-row items-center gap-3 border-b border-card-border px-4 py-4.75 text-xs transition-colors hover:bg-surface-subtle/60 {record.isActive
							? 'border-l-3 border-l-status-processing bg-[#f8fbff]'
							: 'bg-white'}"
					>
						<!-- ID do Registro -->
						<div class="w-34 shrink-0 font-mono text-[11px] text-on-white-secondary">
							{record.id}
						</div>

						<!-- Título -->
						<div class="flex min-w-50 flex-1 flex-col gap-1">
							<span class="text-xs font-semibold text-on-white-main">{record.title}</span>
							<span class="text-[10px] text-on-white-tertiary">{record.url}</span>
						</div>

						<!-- Data/Hora Início -->
						<div class="w-32 shrink-0 leading-tight text-on-white-secondary">
							<p>{record.startDate}</p>
							<p>{record.startTime}</p>
						</div>

						<!-- Data/Hora Fim -->
						<div class="w-32 shrink-0 leading-tight text-on-white-secondary">
							{#if record.endDate && record.endTime}
								<p>{record.endDate}</p>
								<p>{record.endTime}</p>
							{:else}
								<p class="text-on-white-tertiary">—</p>
							{/if}
						</div>

						<!-- Detalhes (resumo) -->
						<div class="flex w-41 shrink-0 flex-col gap-0.75">
							<span class="text-[11px] text-on-white-secondary">{record.detailsSummary}</span>
							<span class="text-[10px] text-on-white-tertiary">{record.detailsMeta}</span>
						</div>

						<!-- Status -->
						<div class="w-47.5 shrink-0">
							<span
								class="inline-flex items-center rounded-md px-2.5 py-1.5 text-[11px] font-medium {style.bg} {style.text}"
							>
								{record.status}
							</span>
						</div>

						<!-- Ações -->
						<div class="w-37.5 shrink-0">
							<button
								type="button"
								class="inline-flex cursor-pointer items-center gap-1.5 text-[11px] font-semibold text-on-white-main transition-colors hover:text-status-processing hover:underline"
							>
								<span>Visualizar Detalhes</span>
								<ArrowUpRight class="size-3.5 shrink-0" />
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Footer -->
		<div
			class="flex flex-row items-center justify-between p-4.5 text-[11px] text-on-white-tertiary"
		>
			<p>Exibindo 1–{filteredRecords.length} de {records.length} registros</p>
			<div class="flex flex-row items-center gap-2">
				<span class="cursor-not-allowed text-on-veridt-blue-muted">Anterior</span>
				<span
					class="flex size-7.5 items-center justify-center rounded-md bg-veridt-blue text-[11px] font-semibold text-white"
				>
					1
				</span>
				<span class="cursor-not-allowed text-on-veridt-blue-muted">Próxima</span>
			</div>
		</div>
	</section>

	<div class="flex flex-row items-center gap-2.5 text-xs text-on-white-tertiary">
		<Info class="size-4 shrink-0 text-on-white-tertiary" />
		<p class="leading-[160%]">
			Registros em andamento não possuem Data/Hora Fim. Relatórios e arquivos ZIP são
			disponibilizados apenas para registros concluídos. Em caso de falha de captura, o crédito é
			estornado.
		</p>
	</div>
</div>
