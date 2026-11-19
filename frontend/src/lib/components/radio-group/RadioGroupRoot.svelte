<script lang="ts">
	import { RadioGroup as BitsRadioGroup, type RadioGroupRootProps } from 'bits-ui';

	let {
		value = $bindable(''),
		orientation = 'horizontal',
		ref = $bindable(null),
		class: className = '',
		children,
		...rest
	}: RadioGroupRootProps = $props();
</script>

<BitsRadioGroup.Root
	bind:value
	bind:ref
	{orientation}
	class="flex flex-row gap-1 rounded-lg bg-surface-canvas p-1 {className}"
	{...rest}
>
	{@render children?.()}
</BitsRadioGroup.Root>
