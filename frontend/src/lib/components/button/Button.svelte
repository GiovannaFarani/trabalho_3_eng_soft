<script lang="ts" module>
	import type { ButtonRootProps } from 'bits-ui';

	export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'link';
	export type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

	export type ButtonProps = ButtonRootProps & {
		variant?: ButtonVariant;
		size?: ButtonSize;
		class?: string;
	};
</script>

<script lang="ts">
	import { Button as BitsButton } from 'bits-ui';

	let {
		variant = 'primary',
		size = 'md',
		class: className = '',
		ref = $bindable(null),
		children,
		...rest
	}: ButtonProps = $props();

	const variantClasses: Record<ButtonVariant, string> = {
		primary:
			'border border-transparent bg-veridt-blue text-white hover:bg-veridt-blue/90 focus-visible:ring-veridt-blue/30',
		secondary:
			'border border-transparent bg-surface-canvas text-on-white-main hover:bg-card-border focus-visible:ring-veridt-blue/20',
		outline:
			'border border-card-border bg-white text-on-white-main hover:bg-surface-subtle focus-visible:ring-veridt-blue/20',
		ghost:
			'border border-transparent bg-transparent text-on-white-secondary hover:bg-surface-canvas hover:text-on-white-main focus-visible:ring-veridt-blue/20',
		link: 'bg-transparent text-on-white-main underline-offset-4 hover:underline focus-visible:ring-veridt-blue/20'
	};

	const sizeClasses: Record<ButtonSize, string> = {
		sm: 'h-9 gap-2 rounded-lg px-3.5 text-xs',
		md: 'h-11.5 gap-2.25 rounded-lg px-4.5 text-[13px]',
		lg: 'h-12 gap-2.25 rounded-lg px-5 text-sm',
		icon: 'size-7 rounded-md p-0 text-xs'
	};

	const linkSizeClasses: Record<ButtonSize, string> = {
		sm: 'h-auto px-0 py-0 text-xs',
		md: 'h-auto px-0 py-0 text-[13px]',
		lg: 'h-auto px-0 py-0 text-sm',
		icon: 'h-auto p-0 text-xs'
	};
</script>

<BitsButton.Root
	bind:ref
	class="inline-flex cursor-pointer items-center justify-center font-semibold transition-colors duration-150 outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 [&_svg]:shrink-0 {variantClasses[
		variant
	]} {variant === 'link' ? linkSizeClasses[size] : sizeClasses[size]} {className}"
	{...rest}
>
	{@render children?.()}
</BitsButton.Root>
