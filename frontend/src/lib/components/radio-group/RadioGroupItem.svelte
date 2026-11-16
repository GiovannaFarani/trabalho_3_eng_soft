<script lang="ts">
	import { RadioGroup as BitsRadioGroup, type RadioGroupItemProps } from 'bits-ui';

	let {
		ref = $bindable(null),
		class: className = '',
		children: userChildren,
		...rest
	}: RadioGroupItemProps = $props();
</script>

<BitsRadioGroup.Item
	bind:ref
	class="flex h-9.25 flex-1 cursor-pointer items-center justify-center gap-1.75 rounded-md text-xs font-medium text-on-white-secondary transition-colors outline-none hover:text-on-white-main focus-visible:ring-2 focus-visible:ring-veridt-blue/20 disabled:cursor-not-allowed disabled:opacity-40 data-[state=checked]:bg-veridt-blue data-[state=checked]:font-semibold data-[state=checked]:text-white {className}"
	{...rest}
>
	{#snippet children(snippetProps)}
		{@render userChildren?.(snippetProps)}
	{/snippet}
</BitsRadioGroup.Item>
