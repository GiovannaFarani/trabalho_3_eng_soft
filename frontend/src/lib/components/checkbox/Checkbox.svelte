<script lang="ts" module>
	import type { CheckboxRootProps } from 'bits-ui';

	export type CheckboxProps = CheckboxRootProps & {
		class?: string;
	};
</script>

<script lang="ts">
	import { Check, Minus } from '@lucide/svelte';
	import { Checkbox as BitsCheckbox } from 'bits-ui';

	let {
		checked = $bindable(false),
		indeterminate = $bindable(false),
		ref = $bindable(null),
		class: className = '',
		children: userChildren,
		...rest
	}: CheckboxProps = $props();
</script>

<BitsCheckbox.Root
	bind:checked
	bind:indeterminate
	bind:ref
	class="flex size-4 shrink-0 cursor-pointer items-center justify-center rounded-[3px] border border-card-border bg-white transition-colors outline-none focus-visible:ring-2 focus-visible:ring-veridt-blue/20 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:border-veridt-blue data-[state=checked]:bg-veridt-blue data-[state=indeterminate]:border-veridt-blue data-[state=indeterminate]:bg-veridt-blue {className}"
	{...rest}
>
	{#snippet children(snippetProps)}
		{#if userChildren}
			{@render userChildren(snippetProps)}
		{:else if snippetProps.indeterminate}
			<Minus class="size-3 text-white" />
		{:else if snippetProps.checked}
			<Check class="size-3 text-white" />
		{/if}
	{/snippet}
</BitsCheckbox.Root>
