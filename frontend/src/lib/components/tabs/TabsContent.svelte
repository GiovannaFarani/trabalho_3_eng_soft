<script lang="ts">
	import { Tabs as BitsTabs, type TabsContentProps } from 'bits-ui';

	let { class: className = '', children, ...rest }: TabsContentProps = $props();
</script>

<BitsTabs.Content class="outline-none {className}" {...rest}>
	{@render children?.()}
</BitsTabs.Content>
