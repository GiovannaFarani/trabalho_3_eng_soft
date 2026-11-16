<script lang="ts">
	import { Tabs as BitsTabs, type TabsListProps } from 'bits-ui';

	let { class: className = '', children, ...rest }: TabsListProps = $props();
</script>

<BitsTabs.List class="flex items-center gap-6 border-b border-card-border {className}" {...rest}>
	{@render children?.()}
</BitsTabs.List>
