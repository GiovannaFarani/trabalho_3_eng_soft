<script lang="ts" module>
	import type { LabelRootProps } from 'bits-ui';

	export type LabelVariant = 'field' | 'inline';

	export type LabelProps = LabelRootProps & {
		variant?: LabelVariant;
		class?: string;
	};
</script>

<script lang="ts">
	import { Label as BitsLabel } from 'bits-ui';

	let {
		variant = 'field',
		class: className = '',
		ref = $bindable(null),
		children,
		...rest
	}: LabelProps = $props();

	const variantClasses: Record<LabelVariant, string> = {
		field: 'text-xs font-semibold text-on-white-secondary',
		inline: 'cursor-pointer text-[11px] leading-[1.6] font-normal text-on-white-secondary'
	};
</script>

<BitsLabel.Root
	bind:ref
	class="peer-disabled:cursor-not-allowed peer-disabled:opacity-50 {variantClasses[
		variant
	]} {className}"
	{...rest}
>
	{@render children?.()}
</BitsLabel.Root>
