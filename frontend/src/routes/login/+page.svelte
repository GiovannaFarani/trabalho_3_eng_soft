<script>
	import { ShieldCheck, ScanLine, FingerprintPattern, LockKeyhole } from '@lucide/svelte';
</script>

<div class="flex flex-row">
	<div class="flex h-dvh w-md min-w-md flex-col justify-between bg-veridt-blue p-11">
		<div class="flex flex-row items-center gap-2.5">
			<ShieldCheck class="size-8.5 text-white" />
			<div class="veridt-text text-white">veridt</div>
		</div>
		<div class="flex flex-col gap-7">
			<p class="text-[11px] text-on-veridt-blue">EVIDÊNCIA. INTEGRIDADE. CONFIANÇA.</p>
			<h1 class="text-white">
				Provas Digitais com Validade Jurídica e Imutabilidade WORM - SHA-256
			</h1>
			<p class="text-sm leading-[170%] text-on-veridt-blue">
				Da captura à preservação, uma cadeia de custódia digital rastreável para advogados e pessoas
				físicas.
			</p>
			<div class="flex flex-row justify-between py-6.25">
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-[#334155] bg-[#1E293B]"
				>
					<ScanLine class="size-8.75 text-on-veridt-blue " />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-[#334155] bg-[#1E293B]"
				>
					<FingerprintPattern class="size-8.75 text-on-veridt-blue " />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-[#334155] bg-[#1E293B]"
				>
					<ShieldCheck class="size-8.75 text-shield-green " />
				</div>
			</div>
			<div class="flex flex-row items-center gap-2">
				<LockKeyhole class="size-4.5 text-shield-green" />
				<p class="text-xs text-[#A7F3D0]">Preservação imutável. Verificação independente.</p>
			</div>
		</div>
		<div>
			<p class="text-[11px] text-[#94A3B8]">© 2026 Veridt</p>
			<p class="text-[11px] text-on-veridt-blue">Termos de uso • Política de privacidade</p>
		</div>
	</div>
	<div class="bg-yellow"></div>
</div>
