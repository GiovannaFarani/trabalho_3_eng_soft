<script lang="ts">
	import { Tabs as BitsTabs, type TabsTriggerProps } from 'bits-ui';

	let { class: className = '', children, ...rest }: TabsTriggerProps = $props();
</script>

<BitsTabs.Trigger
	class="relative -mb-px cursor-pointer appearance-none border-0 border-b-3 border-transparent bg-transparent px-0.5 py-3 text-sm font-medium text-on-white-secondary transition-colors duration-150 outline-none hover:text-on-white-main focus-visible:text-on-white-main disabled:cursor-not-allowed disabled:opacity-40 data-[state=active]:border-veridt-blue data-[state=active]:text-on-white-main {className}"
	{...rest}
>
	{@render children?.()}
</BitsTabs.Trigger>
