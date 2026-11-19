<script lang="ts">
	import {
		ArrowUpRight,
		CalendarDays,
		Check,
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
	import { resolve } from '$app/paths';
	import { Pagination, Popover, Select } from 'bits-ui';
	import {
		ApiError,
		Button,
		Label,
		recordsReaderClient,
		TextInput,
		type EvidenceRecord
	} from '#lib';

	type StatusFilter = 'ALL' | EvidenceRecord['status'];
	type SortOption = 'newest' | 'oldest' | 'title';
	type CompletionFilter = 'all' | 'finished' | 'unfinished';

	const DEFAULT_START_DATE = '';
	const DEFAULT_END_DATE = '';

	let records = $state<EvidenceRecord[]>([]);
	let isLoading = $state(true);
	let hasLoaded = $state(false);
	let loadError = $state<string | null>(null);
	let isAuthError = $state(false);
	let lastUpdatedAt = $state<string | null>(null);

	let searchQuery = $state('');
	let statusFilter = $state<StatusFilter>('ALL');
	let startDateFilter = $state(DEFAULT_START_DATE);
	let endDateFilter = $state(DEFAULT_END_DATE);
	let sortBy = $state<SortOption>('newest');
	let completionFilter = $state<CompletionFilter>('all');
	let currentPage = $state(1);
	let perPage = $state(5);

	let datePopoverOpen = $state(false);
	let filterPopoverOpen = $state(false);

	const statusOptions: { value: StatusFilter; label: string }[] = [
		{ value: 'ALL', label: 'Todos' },
		{ value: 'INICIADO', label: 'Iniciado' },
		{ value: 'PROCESSANDO', label: 'Processando' },
		{ value: 'CONCLUIDO', label: 'Concluído' },
		{ value: 'FALHA - Crédito Estornado', label: 'Falha - Crédito Estornado' }
	];

	const perPageOptions = ['4', '5', '6', '10'];

	function formatIsoLocalDate(date: Date): string {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	function buildDatePresets() {
		const DAY_MS = 24 * 60 * 60 * 1000;
		const now = Date.now();
		const todayIso = formatIsoLocalDate(new Date(now));
		return [
			{ label: 'Todas as datas', start: '', end: '' },
			{ label: 'Hoje', start: todayIso, end: todayIso },
			{
				label: 'Últimos 7 dias',
				start: formatIsoLocalDate(new Date(now - 6 * DAY_MS)),
				end: todayIso
			},
			{
				label: 'Últimos 30 dias',
				start: formatIsoLocalDate(new Date(now - 29 * DAY_MS)),
				end: todayIso
			}
		] as const;
	}

	const datePresets = buildDatePresets();

	function formatCurrentBrasiliaTime(): string {
		return new Intl.DateTimeFormat('pt-BR', {
			timeZone: 'America/Sao_Paulo',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		}).format(new Date());
	}

	function formatMetricCount(count: number): string {
		return String(count).padStart(2, '0');
	}

	const metrics = $derived.by(() => {
		let completed = 0;
		let processing = 0;
		let started = 0;
		let failed = 0;

		for (const record of records) {
			if (record.status === 'CONCLUIDO') completed += 1;
			else if (record.status === 'PROCESSANDO') processing += 1;
			else if (record.status === 'INICIADO') started += 1;
			else if (record.status === 'FALHA - Crédito Estornado') failed += 1;
		}

		return [
			{
				title: 'Registros concluídos',
				value: formatMetricCount(completed),
				description: 'Prontos para consulta',
				icon: FileCheckCorner,
				iconClass: 'text-status-success'
			},
			{
				title: 'Em processamento',
				value: formatMetricCount(processing),
				description: 'Preparando as evidências',
				icon: LoaderCircle,
				iconClass: 'text-status-processing'
			},
			{
				title: 'Sessões iniciadas',
				value: formatMetricCount(started),
				description: 'Gravação em andamento',
				icon: CirclePlay,
				iconClass: 'text-status-warning'
			},
			{
				title: 'Falhas com estorno',
				value: formatMetricCount(failed),
				description: 'Crédito devolvido ao saldo',
				icon: CircleAlert,
				iconClass: 'text-status-danger'
			}
		] as const;
	});

	async function loadRecords(signal?: AbortSignal) {
		isLoading = true;
		loadError = null;
		isAuthError = false;

		try {
			const response = await recordsReaderClient.listRecords({ signal });
			records = response.data;
			hasLoaded = true;
			lastUpdatedAt = formatCurrentBrasiliaTime();
		} catch (error) {
			if (error instanceof DOMException && error.name === 'AbortError') {
				return;
			}
			hasLoaded = false;
			if (error instanceof ApiError) {
				isAuthError = error.status === 401;
				loadError = error.message;
			} else {
				loadError = 'Não foi possível carregar os registros. Tente novamente.';
			}
		} finally {
			if (!signal?.aborted) {
				isLoading = false;
			}
		}
	}

	$effect(() => {
		const controller = new AbortController();
		void loadRecords(controller.signal);
		return () => controller.abort();
	});

	const statusStyles: Record<
		EvidenceRecord['status'],
		{ bg: string; border: string; text: string }
	> = {
		INICIADO: {
			bg: 'bg-amber-50',
			border: 'border-amber-200',
			text: 'text-status-warning'
		},
		PROCESSANDO: {
			bg: 'bg-status-processing-bg',
			border: 'border-blue-200',
			text: 'text-status-processing'
		},
		CONCLUIDO: {
			bg: 'bg-emerald-50',
			border: 'border-emerald-200',
			text: 'text-status-success'
		},
		'FALHA - Crédito Estornado': {
			bg: 'bg-red-50',
			border: 'border-red-200',
			text: 'text-status-danger'
		}
	};

	function toIsoDate(brDate: string): string {
		const parts = brDate.split('/');
		if (parts.length !== 3) return '';
		const [day, month, year] = parts;
		return `${year}-${month}-${day}`;
	}

	function formatBrDate(isoDate: string): string {
		const [year, month, day] = isoDate.split('-');
		return `${day}/${month}/${year}`;
	}

	const selectedStatusLabel = $derived(
		statusOptions.find((option) => option.value === statusFilter)?.label ?? 'Todos'
	);

	const dateRangeLabel = $derived.by(() => {
		if (startDateFilter && endDateFilter) {
			return startDateFilter === endDateFilter
				? formatBrDate(startDateFilter)
				: `${formatBrDate(startDateFilter)} – ${formatBrDate(endDateFilter)}`;
		}
		if (startDateFilter) return `A partir de ${formatBrDate(startDateFilter)}`;
		if (endDateFilter) return `Até ${formatBrDate(endDateFilter)}`;
		return 'Todas as datas';
	});

	const extraFiltersCount = $derived(
		(sortBy !== 'newest' ? 1 : 0) + (completionFilter !== 'all' ? 1 : 0)
	);

	const hasAnyActiveFilter = $derived(
		searchQuery.trim() !== '' ||
			statusFilter !== 'ALL' ||
			startDateFilter !== DEFAULT_START_DATE ||
			endDateFilter !== DEFAULT_END_DATE ||
			sortBy !== 'newest' ||
			completionFilter !== 'all'
	);

	const filteredRecords = $derived.by(() => {
		const query = searchQuery.trim().toLowerCase();

		const matches = records.filter((record) => {
			if (query) {
				const matchesQuery =
					record.id.toLowerCase().includes(query) ||
					record.title.toLowerCase().includes(query) ||
					record.url.toLowerCase().includes(query);
				if (!matchesQuery) return false;
			}

			if (statusFilter !== 'ALL' && record.status !== statusFilter) {
				return false;
			}

			const recordIsoDate = toIsoDate(record.startDate);
			if (startDateFilter && recordIsoDate < startDateFilter) return false;
			if (endDateFilter && recordIsoDate > endDateFilter) return false;

			if (completionFilter === 'finished' && !record.endDate) return false;
			if (completionFilter === 'unfinished' && record.endDate) return false;

			return true;
		});

		return [...matches].sort((a, b) => {
			if (sortBy === 'title') {
				return a.title.localeCompare(b.title, 'pt-BR');
			}
			const aTimestamp = `${toIsoDate(a.startDate)}T${a.startTime}`;
			const bTimestamp = `${toIsoDate(b.startDate)}T${b.startTime}`;
			return sortBy === 'oldest'
				? aTimestamp.localeCompare(bTimestamp)
				: bTimestamp.localeCompare(aTimestamp);
		});
	});

	const totalPages = $derived(Math.max(1, Math.ceil(filteredRecords.length / perPage)));
	const safePage = $derived(Math.min(currentPage, totalPages));

	const paginatedRecords = $derived(
		filteredRecords.slice((safePage - 1) * perPage, safePage * perPage)
	);

	function resetAllFilters() {
		searchQuery = '';
		statusFilter = 'ALL';
		startDateFilter = DEFAULT_START_DATE;
		endDateFilter = DEFAULT_END_DATE;
		sortBy = 'newest';
		completionFilter = 'all';
		currentPage = 1;
	}
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

	{#if hasLoaded && !loadError}
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
	{/if}

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
					{filteredRecords.length}
					{filteredRecords.length === 1 ? 'registro' : 'registros'}
				</span>
			</div>

			<button
				type="button"
				disabled={isLoading}
				onclick={() => void loadRecords()}
				class="flex cursor-pointer flex-row items-center gap-1.75 text-[11px] text-on-white-tertiary transition-colors hover:text-on-white-main disabled:cursor-not-allowed disabled:opacity-60"
			>
				<RefreshCw class="size-3.5 {isLoading ? 'animate-spin' : ''}" />
				<span>
					{#if isLoading}
						Atualizando...
					{:else if lastUpdatedAt}
						Atualizado às {lastUpdatedAt}
					{:else}
						Atualizar
					{/if}
				</span>
			</button>
		</div>

		<div class="flex flex-row flex-wrap items-center gap-3 px-5 pb-5">
			<TextInput
				type="search"
				placeholder="Buscar por título, URL ou ID do registro"
				bind:value={searchQuery}
				oninput={() => (currentPage = 1)}
				wrapperClass="flex-1 min-w-65"
				class="h-11.5!"
			>
				{#snippet leading()}
					<Search class="size-4" />
				{/snippet}
			</TextInput>

			<Select.Root
				type="single"
				items={statusOptions}
				bind:value={statusFilter}
				onValueChange={() => (currentPage = 1)}
			>
				<Select.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="outline" class="justify-between">
							<ChevronDown class="size-4 text-on-white-secondary" />
							<span>Status: {selectedStatusLabel}</span>
						</Button>
					{/snippet}
				</Select.Trigger>
				<Select.Portal>
					<Select.Content
						sideOffset={6}
						align="end"
						class="z-50 min-w-56 rounded-xl border border-card-border bg-white p-1.5 shadow-lg"
					>
						<Select.Viewport class="flex flex-col gap-0.5">
							{#each statusOptions as option (option.value)}
								<Select.Item
									value={option.value}
									label={option.label}
									class="flex cursor-pointer items-center justify-between gap-2 rounded-lg px-3 py-2 text-xs text-on-white-main transition-colors outline-none data-highlighted:bg-surface-subtle data-selected:bg-surface-canvas data-selected:font-semibold"
								>
									{#snippet children({ selected })}
										<span>{option.label}</span>
										{#if selected}
											<Check class="size-3.5 text-status-processing" />
										{/if}
									{/snippet}
								</Select.Item>
							{/each}
						</Select.Viewport>
					</Select.Content>
				</Select.Portal>
			</Select.Root>

			<Popover.Root bind:open={datePopoverOpen}>
				<Popover.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="outline">
							<CalendarDays class="size-4 text-on-white-secondary" />
							<span>{dateRangeLabel}</span>
						</Button>
					{/snippet}
				</Popover.Trigger>
				<Popover.Portal>
					<Popover.Content
						sideOffset={6}
						align="end"
						class="z-50 flex w-80 flex-col gap-4 rounded-xl border border-card-border bg-white p-4 shadow-lg"
					>
						<div class="flex flex-col gap-2">
							<p class="text-xs font-semibold text-on-white-main">Período de captura</p>
							<div class="flex flex-wrap gap-1.5">
								{#each datePresets as preset (preset.label)}
									{@const isSelected =
										startDateFilter === preset.start && endDateFilter === preset.end}
									<button
										type="button"
										onclick={() => {
											startDateFilter = preset.start;
											endDateFilter = preset.end;
											currentPage = 1;
										}}
										class="cursor-pointer rounded-md border px-2.5 py-1 text-[11px] font-medium transition-colors {isSelected
											? 'border-veridt-blue bg-veridt-blue text-white'
											: 'border-card-border bg-surface-subtle text-on-white-secondary hover:bg-surface-canvas hover:text-on-white-main'}"
									>
										{preset.label}
									</button>
								{/each}
							</div>
						</div>

						<div class="grid grid-cols-2 gap-3">
							<div class="flex flex-col gap-1.5">
								<Label for="filter-start-date">Data inicial</Label>
								<input
									id="filter-start-date"
									type="date"
									bind:value={startDateFilter}
									max={endDateFilter || undefined}
									onchange={() => (currentPage = 1)}
									class="h-9.5 rounded-lg border border-card-border bg-white px-2.5 text-xs text-on-white-ink outline-none focus:border-veridt-blue focus:ring-2 focus:ring-veridt-blue/15"
								/>
							</div>
							<div class="flex flex-col gap-1.5">
								<Label for="filter-end-date">Data final</Label>
								<input
									id="filter-end-date"
									type="date"
									bind:value={endDateFilter}
									min={startDateFilter || undefined}
									onchange={() => (currentPage = 1)}
									class="h-9.5 rounded-lg border border-card-border bg-white px-2.5 text-xs text-on-white-ink outline-none focus:border-veridt-blue focus:ring-2 focus:ring-veridt-blue/15"
								/>
							</div>
						</div>

						<div
							class="flex flex-row items-center justify-between border-t border-card-border pt-3"
						>
							<Button
								type="button"
								variant="ghost"
								size="sm"
								onclick={() => {
									startDateFilter = '';
									endDateFilter = '';
									currentPage = 1;
								}}
							>
								Limpar datas
							</Button>
							<Button type="button" size="sm" onclick={() => (datePopoverOpen = false)}>
								Aplicar
							</Button>
						</div>
					</Popover.Content>
				</Popover.Portal>
			</Popover.Root>

			<Popover.Root bind:open={filterPopoverOpen}>
				<Popover.Trigger>
					{#snippet child({ props })}
						<Button {...props} variant="outline">
							<SlidersHorizontal class="size-4 text-on-white-secondary" />
							<span>Filtrar</span>
							{#if extraFiltersCount > 0}
								<span
									class="flex size-4.5 items-center justify-center rounded-full bg-veridt-blue text-[10px] font-semibold text-white"
								>
									{extraFiltersCount}
								</span>
							{/if}
						</Button>
					{/snippet}
				</Popover.Trigger>
				<Popover.Portal>
					<Popover.Content
						sideOffset={6}
						align="end"
						class="z-50 flex w-72 flex-col gap-4 rounded-xl border border-card-border bg-white p-4 shadow-lg"
					>
						<div class="flex flex-col gap-2">
							<p class="text-xs font-semibold text-on-white-main">Ordenação</p>
							<div class="flex flex-col gap-1">
								{#each [{ value: 'newest', label: 'Mais recentes primeiro' }, { value: 'oldest', label: 'Mais antigos primeiro' }, { value: 'title', label: 'Título (A–Z)' }] as item (item.value)}
									<button
										type="button"
										onclick={() => {
											sortBy = item.value as SortOption;
											currentPage = 1;
										}}
										class="flex cursor-pointer items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-colors {sortBy ===
										item.value
											? 'bg-surface-canvas font-semibold text-on-white-main'
											: 'text-on-white-secondary hover:bg-surface-subtle hover:text-on-white-main'}"
									>
										<span>{item.label}</span>
										{#if sortBy === item.value}
											<Check class="size-3.5 text-status-processing" />
										{/if}
									</button>
								{/each}
							</div>
						</div>

						<div class="flex flex-col gap-2 border-t border-card-border pt-3">
							<p class="text-xs font-semibold text-on-white-main">Finalização da captura</p>
							<div class="flex flex-col gap-1">
								{#each [{ value: 'all', label: 'Todos os registros' }, { value: 'finished', label: 'Apenas com Data/Hora Fim' }, { value: 'unfinished', label: 'Em andamento ou falha' }] as item (item.value)}
									<button
										type="button"
										onclick={() => {
											completionFilter = item.value as CompletionFilter;
											currentPage = 1;
										}}
										class="flex cursor-pointer items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-colors {completionFilter ===
										item.value
											? 'bg-surface-canvas font-semibold text-on-white-main'
											: 'text-on-white-secondary hover:bg-surface-subtle hover:text-on-white-main'}"
									>
										<span>{item.label}</span>
										{#if completionFilter === item.value}
											<Check class="size-3.5 text-status-processing" />
										{/if}
									</button>
								{/each}
							</div>
						</div>

						<div
							class="flex flex-row items-center justify-between border-t border-card-border pt-3"
						>
							<Button
								type="button"
								variant="ghost"
								size="sm"
								disabled={!hasAnyActiveFilter}
								onclick={() => {
									resetAllFilters();
									filterPopoverOpen = false;
								}}
							>
								Limpar tudo
							</Button>
							<Button type="button" size="sm" onclick={() => (filterPopoverOpen = false)}>
								Fechar
							</Button>
						</div>
					</Popover.Content>
				</Popover.Portal>
			</Popover.Root>
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

				{#if isLoading && records.length === 0}
					<div
						class="flex flex-col items-center justify-center gap-3 border-b border-card-border px-4 py-12 text-center"
					>
						<LoaderCircle class="size-5 animate-spin text-status-processing" />
						<p class="text-sm font-medium text-on-white-main">Carregando registros...</p>
						<p class="text-xs text-on-white-tertiary">
							Consultando suas evidências no serviço de registros.
						</p>
					</div>
				{:else if loadError}
					<div
						role="alert"
						class="flex flex-col items-center justify-center gap-3 border-b border-card-border px-4 py-12 text-center"
					>
						<CircleAlert class="size-5 text-status-danger" />
						<p class="text-sm font-medium text-on-white-main">
							{isAuthError
								? 'Sessão necessária para consultar registros'
								: 'Erro ao carregar registros'}
						</p>
						<p class="max-w-md text-xs text-on-white-tertiary">{loadError}</p>
						<div class="flex flex-row items-center gap-2">
							{#if isAuthError}
								<a
									href={resolve('/login')}
									class="inline-flex h-8.5 items-center justify-center rounded-lg bg-veridt-blue px-3.5 text-xs font-semibold text-white transition-colors hover:bg-veridt-blue/90"
								>
									Ir para Login
								</a>
							{/if}
							<Button type="button" variant="outline" size="sm" onclick={() => void loadRecords()}>
								Tentar novamente
							</Button>
						</div>
					</div>
				{:else if paginatedRecords.length === 0}
					<div
						class="flex flex-col items-center justify-center gap-3 border-b border-card-border px-4 py-12 text-center"
					>
						<p class="text-sm font-medium text-on-white-main">
							{#if records.length === 0}
								Nenhum registro realizado até o momento.
							{:else}
								Nenhum registro encontrado com os filtros selecionados.
							{/if}
						</p>
						<p class="text-xs text-on-white-tertiary">
							{#if records.length === 0}
								Assim que você iniciar uma captura, ela aparecerá aqui.
							{:else}
								Ajuste a busca, o status ou o período para visualizar outros registros.
							{/if}
						</p>
						{#if hasAnyActiveFilter}
							<Button type="button" variant="outline" size="sm" onclick={resetAllFilters}>
								Limpar filtros
							</Button>
						{/if}
					</div>
				{:else}
					{#each paginatedRecords as record (record.id)}
						{@const style = statusStyles[record.status]}
						<div
							class="flex flex-row items-center gap-3 border-b border-card-border bg-white px-4 py-4.75 text-xs transition-[background-color,box-shadow] duration-150 hover:bg-row-hover hover:shadow-[inset_3px_0_0_0_var(--color-status-processing)]"
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
									class="inline-flex items-center rounded-md border px-2.5 py-1.5 text-[11px] font-medium {style.bg} {style.border} {style.text}"
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
				{/if}
			</div>
		</div>

		<!-- Footer / Pagination -->
		<Pagination.Root
			count={filteredRecords.length}
			{perPage}
			page={safePage}
			onPageChange={(page) => (currentPage = page)}
		>
			{#snippet children({ pages, range })}
				<div
					class="flex flex-row flex-wrap items-center justify-between gap-4 p-4.5 text-[11px] text-on-white-tertiary"
				>
					<div class="flex flex-row items-center gap-3">
						<p>
							{#if filteredRecords.length === 0}
								Exibindo 0 de {records.length} registros
							{:else}
								Exibindo {range.start}–{range.end} de {filteredRecords.length}
								{filteredRecords.length === 1 ? 'registro' : 'registros'}
							{/if}
						</p>

						<Select.Root
							type="single"
							value={String(perPage)}
							items={perPageOptions.map((value) => ({ value, label: `${value} por página` }))}
							onValueChange={(value) => {
								perPage = Number(value);
								currentPage = 1;
							}}
						>
							<Select.Trigger
								class="inline-flex cursor-pointer items-center gap-1 rounded-md border border-card-border bg-white px-2 py-1 text-[11px] text-on-white-secondary transition-colors hover:bg-surface-subtle hover:text-on-white-main"
							>
								<span>{perPage} / pág</span>
								<ChevronDown class="size-3" />
							</Select.Trigger>
							<Select.Portal>
								<Select.Content
									sideOffset={4}
									align="start"
									class="z-50 min-w-28 rounded-lg border border-card-border bg-white p-1 shadow-lg"
								>
									<Select.Viewport class="flex flex-col gap-0.5">
										{#each perPageOptions as option (option)}
											<Select.Item
												value={option}
												label="{option} por página"
												class="flex cursor-pointer items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-[11px] text-on-white-main outline-none data-highlighted:bg-surface-subtle data-selected:bg-surface-canvas data-selected:font-semibold"
											>
												{#snippet children({ selected })}
													<span>{option} por página</span>
													{#if selected}
														<Check class="size-3 text-status-processing" />
													{/if}
												{/snippet}
											</Select.Item>
										{/each}
									</Select.Viewport>
								</Select.Content>
							</Select.Portal>
						</Select.Root>
					</div>

					<div class="flex flex-row items-center gap-1.5">
						<Pagination.PrevButton
							class="cursor-pointer rounded-md px-2 py-1.5 text-[11px] font-medium text-on-white-secondary transition-colors hover:bg-surface-subtle hover:text-on-white-main disabled:cursor-not-allowed disabled:text-on-veridt-blue-muted disabled:hover:bg-transparent"
						>
							Anterior
						</Pagination.PrevButton>

						{#each pages as page (page.key)}
							{#if page.type === 'ellipsis'}
								<span class="px-1 text-on-white-tertiary">…</span>
							{:else}
								<Pagination.Page
									{page}
									class="flex size-7.5 cursor-pointer items-center justify-center rounded-md border border-card-border bg-white text-[11px] font-semibold text-on-white-secondary transition-colors hover:bg-surface-subtle hover:text-on-white-main data-selected:border-veridt-blue data-selected:bg-veridt-blue data-selected:text-white"
								>
									{page.value}
								</Pagination.Page>
							{/if}
						{/each}

						<Pagination.NextButton
							class="cursor-pointer rounded-md px-2 py-1.5 text-[11px] font-medium text-on-white-secondary transition-colors hover:bg-surface-subtle hover:text-on-white-main disabled:cursor-not-allowed disabled:text-on-veridt-blue-muted disabled:hover:bg-transparent"
						>
							Próxima
						</Pagination.NextButton>
					</div>
				</div>
			{/snippet}
		</Pagination.Root>
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
