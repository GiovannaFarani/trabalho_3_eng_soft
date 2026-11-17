<script lang="ts" module>
	import type { Snippet } from 'svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	export type TextInputType = 'text' | 'email' | 'password' | 'search' | 'tel' | 'url' | 'number';

	export type TextInputProps = Omit<HTMLInputAttributes, 'type' | 'value' | 'class'> & {
		value?: string;
		type?: TextInputType;
		label?: string;
		hint?: string;
		error?: string;
		class?: string;
		wrapperClass?: string;
		ref?: HTMLInputElement | null;
		leading?: Snippet;
		trailing?: Snippet;
	};
</script>

<script lang="ts">
	import { Label } from '../label/index.ts';

	const generatedId = $props.id();

	let {
		value = $bindable(''),
		type = 'text',
		label,
		hint,
		error,
		id,
		class: className = '',
		wrapperClass = '',
		ref = $bindable(null),
		leading,
		trailing,
		...rest
	}: TextInputProps = $props();

	const inputId = $derived(id ?? generatedId);
	const messageId = $derived(error || hint ? `${inputId}-message` : undefined);
</script>

<div class="flex flex-col gap-1.75 {wrapperClass}">
	{#if label}
		<Label for={inputId}>{label}</Label>
	{/if}

	<div class="relative flex items-center">
		{#if leading}
			<div
				class="pointer-events-none absolute left-3 flex items-center text-on-white-tertiary"
				aria-hidden="true"
			>
				{@render leading()}
			</div>
		{/if}

		<input
			bind:this={ref}
			bind:value
			id={inputId}
			{type}
			aria-invalid={error ? true : undefined}
			aria-describedby={messageId}
			class="peer h-11 w-full rounded-lg border bg-white text-[13px] font-normal text-on-white-ink transition-colors duration-150 placeholder:text-on-white-tertiary focus:ring-2 focus:outline-none disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:opacity-60 {leading
				? 'pl-9'
				: 'pl-3'} {trailing ? 'pr-10' : 'pr-3'} {error
				? 'border-red-500 focus:border-red-500 focus:ring-red-500/15'
				: 'border-card-border focus:border-veridt-blue focus:ring-veridt-blue/15'} {className}"
			{...rest}
		/>

		{#if trailing}
			<div class="absolute right-2 flex items-center text-on-white-tertiary">
				{@render trailing()}
			</div>
		{/if}
	</div>

	{#if error}
		<p id={messageId} class="text-[11px] text-red-600">{error}</p>
	{:else if hint}
		<p id={messageId} class="text-[11px] text-on-white-tertiary">{hint}</p>
	{/if}
</div>
