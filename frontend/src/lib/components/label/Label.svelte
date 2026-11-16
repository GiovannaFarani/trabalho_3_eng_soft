<script lang="ts" module>
	import type { LabelRootProps } from 'bits-ui';

	export type LabelProps = LabelRootProps & {
		class?: string;
	};
</script>

<script lang="ts">
	import { Label as BitsLabel } from 'bits-ui';

	let { class: className = '', ref = $bindable(null), children, ...rest }: LabelProps = $props();
</script>

<BitsLabel.Root
	bind:ref
	class="text-xs font-semibold text-on-white-secondary peer-disabled:cursor-not-allowed peer-disabled:opacity-50 {className}"
	{...rest}
>
	{@render children?.()}
</BitsLabel.Root>
