<script lang="ts">
	import { Plus } from '@lucide/svelte';
	import { Button } from '#lib';
</script>

<div class="flex flex-row items-center justify-between gap-6">
	<div class="flex flex-col gap-2.25">
		<p class="text-xs text-on-white-tertiary">Área de trabalho / Meus Registros</p>
		<h1 class="text-[28px]! leading-tight! font-bold! text-on-white-main">Registros Realizados</h1>
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
