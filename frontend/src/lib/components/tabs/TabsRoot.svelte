<script lang="ts">
	import { Tabs as BitsTabs, type TabsRootProps } from 'bits-ui';

	let { value = $bindable(''), class: className = '', children, ...rest }: TabsRootProps = $props();
</script>

<BitsTabs.Root bind:value class="flex flex-col {className}" {...rest}>
	{@render children?.()}
</BitsTabs.Root>
