<script lang="ts">
	import { CircleAlert, CirclePlay, FileCheckCorner, LoaderCircle, Plus } from '@lucide/svelte';
	import { Button } from '#lib';

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
</div>
