<script lang="ts">
	import {
		CircleQuestionMark,
		FolderLock,
		LockKeyhole,
		LogOut,
		ScanLine,
		ShieldCheck,
		Wallet
	} from '@lucide/svelte';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { ScrollArea } from '#lib';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	const navItems = [
		{
			label: 'Novo Registro',
			icon: ScanLine,
			href: null
		},
		{
			label: 'Meus Registros',
			icon: FolderLock,
			href: resolve('/(workspace)/records')
		},
		{
			label: 'Comprar Créditos',
			icon: Wallet,
			href: null
		}
	] as const;
</script>

<div class="flex h-dvh flex-row overflow-hidden bg-surface-canvas">
	<aside
		class="flex h-full w-56 shrink-0 flex-col justify-between gap-8 overflow-y-auto bg-veridt-blue px-4.5 pt-6.75 pb-7"
	>
		<div class="flex flex-col gap-10.5">
			<div class="flex flex-row items-center gap-2.5 pl-3">
				<ShieldCheck class="size-8.5 text-white" />
				<div class="veridt-text text-white">veridt</div>
			</div>

			<nav class="flex flex-col gap-2" aria-label="Área de trabalho">
				<p class="text-[10px] font-semibold text-on-veridt-blue-muted">ÁREA DE TRABALHO</p>

				{#each navItems as item (item.label)}
					{@const Icon = item.icon}
					{@const isActive = item.href !== null && page.url.pathname.startsWith(item.href)}
					{#if item.href}
						<a
							href={item.href}
							class="flex h-11.5 flex-row items-center gap-2.75 rounded-lg px-3 text-[13px] transition-colors {isActive
								? 'bg-veridt-blue-surface font-semibold text-white'
								: 'font-normal text-on-veridt-blue hover:bg-veridt-blue-surface/60 hover:text-white'}"
						>
							<Icon class="size-4.5 shrink-0" />
							<span>{item.label}</span>
						</a>
					{:else}
						<button
							type="button"
							class="flex h-11.5 cursor-pointer flex-row items-center gap-2.75 rounded-lg px-3 text-left text-[13px] font-normal text-on-veridt-blue transition-colors hover:bg-veridt-blue-surface/60 hover:text-white"
						>
							<Icon class="size-4.5 shrink-0" />
							<span>{item.label}</span>
						</button>
					{/if}
				{/each}
			</nav>
		</div>

		<div class="flex flex-col gap-5.5">
			<div class="flex flex-col gap-2.25 rounded-lg bg-veridt-blue-surface p-3.75">
				<ShieldCheck class="size-5.75 text-shield-green" />
				<p class="text-xs font-semibold text-white">Integridade por padrão</p>
				<p class="text-[11px] leading-[160%] text-on-veridt-blue">
					Evidências com SHA-256 e armazenamento imutável WORM.
				</p>
			</div>

			<button
				type="button"
				class="flex cursor-pointer flex-row items-center gap-2.25 text-left text-xs text-on-veridt-blue transition-colors hover:text-white"
			>
				<CircleQuestionMark class="size-4 shrink-0" />
				<span>Central de ajuda</span>
			</button>

			<p class="text-[10px] text-on-veridt-blue-muted">VERIDT • AMBIENTE SEGURO</p>
		</div>
	</aside>

	<div class="flex h-full min-w-0 flex-1 flex-col overflow-hidden">
		<header
			class="flex h-20 shrink-0 flex-row items-center justify-between border-b border-card-border bg-white px-10"
		>
			<div class="flex flex-row items-center gap-2.25">
				<LockKeyhole class="size-3.75 text-on-white-secondary" />
				<p class="text-xs text-on-white-secondary">Ambiente de evidências digitais</p>
			</div>

			<div class="flex flex-row items-center gap-5.5">
				<div class="rounded-md bg-surface-subtle px-2.5 py-1.5 text-[11px] text-on-white-secondary">
					Saldo: 12 Créditos
				</div>

				<div class="flex flex-row items-center gap-2.5">
					<div
						class="flex size-8.25 items-center justify-center rounded-full bg-surface-subtle text-[11px] text-on-white-main"
					>
						FS
					</div>
					<span class="text-xs text-on-white-ink">Dr. Fulano da Silva - OAB/BA</span>
				</div>

				<a
					href={resolve('/login')}
					class="flex flex-row items-center gap-1.75 text-xs text-on-white-secondary transition-colors hover:text-on-white-main"
				>
					<LogOut class="size-3.75" />
					<span>Sair do Sistema</span>
				</a>
			</div>
		</header>

		<ScrollArea
			class="min-h-0 flex-1"
			viewportClass="[&>[data-scroll-area-content]]:flex [&>[data-scroll-area-content]]:flex-col [&>[data-scroll-area-content]]:justify-between"
		>
			<main class="flex flex-col gap-7 p-10">
				{@render children()}
			</main>

			<footer
				class="flex shrink-0 flex-row items-center justify-between px-10 pt-1 pb-7 text-[11px] text-on-white-tertiary"
			>
				<p>© 2026 Veridt. Todos os direitos reservados.</p>
				<p>Horários em Brasília • UTC−03:00</p>
			</footer>
		</ScrollArea>
	</div>
</div>
