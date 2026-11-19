<script lang="ts" module>
	import type { ScrollAreaRootProps, ScrollAreaType } from 'bits-ui';

	export type ScrollAreaOrientation = 'vertical' | 'horizontal' | 'both';

	export type ScrollAreaProps = ScrollAreaRootProps & {
		orientation?: ScrollAreaOrientation;
		type?: ScrollAreaType;
		class?: string;
		viewportClass?: string;
		scrollbarClass?: string;
	};
</script>

<script lang="ts">
	import { ScrollArea as BitsScrollArea } from 'bits-ui';

	let {
		orientation = 'vertical',
		type = 'auto',
		ref = $bindable(null),
		class: className = '',
		viewportClass = '',
		scrollbarClass = '',
		children,
		...rest
	}: ScrollAreaProps = $props();
</script>

<BitsScrollArea.Root
	bind:ref
	{type}
	class="relative flex flex-col overflow-hidden {className}"
	{...rest}
>
	<BitsScrollArea.Viewport class="min-h-0 w-full flex-1 {viewportClass}">
		{@render children?.()}
	</BitsScrollArea.Viewport>

	{#if orientation === 'vertical' || orientation === 'both'}
		<BitsScrollArea.Scrollbar
			orientation="vertical"
			class="absolute flex w-2.5 touch-none p-0.5 transition-colors select-none {scrollbarClass}"
		>
			<BitsScrollArea.Thumb
				class="relative flex-1 rounded-full bg-control-border transition-colors hover:bg-on-white-tertiary"
			/>
		</BitsScrollArea.Scrollbar>
	{/if}

	{#if orientation === 'horizontal' || orientation === 'both'}
		<BitsScrollArea.Scrollbar
			orientation="horizontal"
			class="absolute flex h-2.5 touch-none flex-col p-0.5 transition-colors select-none {scrollbarClass}"
		>
			<BitsScrollArea.Thumb
				class="relative flex-1 rounded-full bg-control-border transition-colors hover:bg-on-white-tertiary"
			/>
		</BitsScrollArea.Scrollbar>
	{/if}

	{#if orientation === 'both'}
		<BitsScrollArea.Corner />
	{/if}
</BitsScrollArea.Root>
