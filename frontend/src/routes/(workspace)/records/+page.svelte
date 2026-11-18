<script lang="ts">
	import {
		CalendarDays,
		ChevronDown,
		CircleAlert,
		CirclePlay,
		FileCheckCorner,
		LoaderCircle,
		Plus,
		RefreshCw,
		Search,
		SlidersHorizontal
	} from '@lucide/svelte';
	import { Button, TextInput } from '#lib';

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
		class="flex flex-col rounded-xl border border-card-border bg-white"
		aria-label="Registros"
	>
		<div class="flex flex-row items-center justify-between px-5 pt-5.5 pb-4.5">
			<div class="flex flex-row items-center gap-2.5">
				<h2 class="text-base! font-normal! text-on-white-main">Todos os registros</h2>
				<span
					class="rounded-md bg-surface-subtle px-2.5 py-1.5 text-[11px] text-on-white-secondary"
				>
					6 registros
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
	</section>
</div>
