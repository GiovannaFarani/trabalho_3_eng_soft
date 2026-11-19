<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { authSession } from '#lib';

	$effect(() => {
		const destination = authSession.isAuthenticated
			? resolve('/(workspace)/records')
			: resolve('/login');
		void goto(destination, { replaceState: true });
	});
</script>

<div
	class="flex h-dvh items-center justify-center bg-surface-canvas text-xs text-on-white-tertiary"
>
	Redirecionando...
</div>
