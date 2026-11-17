<script lang="ts">
	import {
		ShieldCheck,
		ScanLine,
		FingerprintPattern,
		LockKeyhole,
		CircleQuestionMark,
		Eye,
		EyeOff,
		ArrowRight,
		Scale,
		Info,
		Shield,
		KeyRound,
		Mail
	} from '@lucide/svelte';
	import { Button, Checkbox, Label, RadioGroup, ScrollArea, Tabs, TextInput } from '#lib';

	let email = $state('');
	let password = $state('');
	let showPassword = $state(false);
	let isRecoveringPassword = $state(false);
	let recoveryEmail = $state('');

	let profileType = $state<'lawyer' | 'individual'>('lawyer');
	let fullName = $state('');
	let registerEmail = $state('');
	let cpf = $state('');
	let oabNumber = $state('');
	let registerPassword = $state('');
	let showRegisterPassword = $state(false);
	let acceptedTerms = $state(false);

	const termsId = $props.id();
</script>

<div class="flex h-dvh flex-row overflow-hidden">
	<div
		class="flex h-full w-md min-w-md shrink-0 flex-col justify-between overflow-y-auto bg-veridt-blue p-11"
	>
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
					<ScanLine class="size-8.75 text-on-veridt-blue" />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-[#334155] bg-[#1E293B]"
				>
					<FingerprintPattern class="size-8.75 text-on-veridt-blue" />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-[#334155] bg-[#1E293B]"
				>
					<ShieldCheck class="size-8.75 text-shield-green" />
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
	<div class="flex h-full min-w-0 flex-1 flex-col gap-7 overflow-hidden px-11 pt-13 pb-8">
		<div class="flex shrink-0 flex-col">
			<div class="flex flex-row justify-between">
				<p class="text-[11px] text-on-white-tertiary">ACESSO À PLATAFORMA</p>
				<div class="flex flex-row items-center gap-1.5">
					<CircleQuestionMark class="size-4 text-on-white-tertiary" />
					<p class="text-xs text-on-white-tertiary">Precisa de ajuda?</p>
				</div>
			</div>
			<h2 class="text-on-white-main">Sua evidência começa aqui.</h2>
			<p class="text-sm text-on-white-secondary">
				Entre na sua conta ou crie um perfil para iniciar seus registros.
			</p>
		</div>
		<div
			class="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-card-border bg-white"
		>
			<Tabs.Root value="login" class="min-h-0 flex-1">
				<Tabs.List class="shrink-0">
					<Tabs.Trigger class="ml-7 py-4.5" value="login">Entrar</Tabs.Trigger>
					<Tabs.Trigger class="py-4.5" value="register">Cadastrar Usuário</Tabs.Trigger>
					<div class="mr-7 ml-auto flex flex-row items-center gap-1.5">
						<LockKeyhole class="size-3.25 text-on-white-tertiary" />
						<p class="text-[11px] text-on-white-tertiary">Conexão protegida</p>
					</div>
				</Tabs.List>
				<Tabs.Content value="login" class="min-h-0 flex-1 flex-col data-[state=active]:flex">
					<ScrollArea class="min-h-0 flex-1" viewportClass="p-7">
						{#if isRecoveringPassword}
							<form
								class="flex flex-col gap-4 rounded-xl border border-card-border bg-[#f8fafc] p-5"
								onsubmit={(e) => e.preventDefault()}
							>
								<div class="flex flex-row items-center gap-2.25">
									<KeyRound class="size-4.5 text-on-white-main" />
									<p class="text-[15px] text-on-white-main">Recuperar Senha</p>
								</div>
								<p class="text-xs leading-[160%] text-on-white-secondary">
									Informe o e-mail da sua conta. Enviaremos um link para definir uma nova senha.
								</p>
								<TextInput
									label="E-mail de recuperação"
									type="email"
									placeholder="fulano@exemplo.com.br"
									autocomplete="email"
									bind:value={recoveryEmail}
								/>
								<Button type="submit" variant="outline" class="w-full">
									<Mail class="size-4" />
									Enviar link de recuperação
								</Button>
								<Button
									type="button"
									variant="link"
									size="sm"
									class="self-start text-[11px]! font-normal! text-on-white-tertiary! hover:text-on-white-main!"
									onclick={() => (isRecoveringPassword = false)}
								>
									Voltar para Entrar
								</Button>
							</form>
						{:else}
							<form class="flex flex-col gap-4.75" onsubmit={(e) => e.preventDefault()}>
								<div class="flex flex-col gap-1.5">
									<h3 class="text-on-white-main">Bem-vindo de volta</h3>
									<p class="text-xs leading-[150%] text-on-white-tertiary">
										Use seu e-mail e senha para continuar.
									</p>
								</div>
								<TextInput
									label="E-mail"
									type="email"
									placeholder="fulano@exemplo.com.br"
									autocomplete="email"
									bind:value={email}
								/>
								<TextInput
									label="Senha"
									type={showPassword ? 'text' : 'password'}
									placeholder="••••••••••••"
									autocomplete="current-password"
									bind:value={password}
								>
									{#snippet trailing()}
										<Button
											type="button"
											variant="ghost"
											size="icon"
											class="text-on-white-tertiary hover:text-on-white-main"
											aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
											onclick={() => (showPassword = !showPassword)}
										>
											{#if showPassword}
												<Eye class="size-4" />
											{:else}
												<EyeOff class="size-4" />
											{/if}
										</Button>
									{/snippet}
								</TextInput>
								<div class="flex flex-col gap-1.75">
									<Button
										type="button"
										variant="link"
										size="sm"
										class="self-start"
										onclick={() => (isRecoveringPassword = true)}
									>
										Esqueci minha senha / Recuperar Senha
									</Button>
								</div>
								<Button type="submit" class="w-full">
									<ArrowRight class="size-4" />
									Entrar no Sistema
								</Button>
							</form>
						{/if}
					</ScrollArea>
				</Tabs.Content>
				<Tabs.Content value="register" class="min-h-0 flex-1 flex-col data-[state=active]:flex">
					<ScrollArea class="min-h-0 flex-1" viewportClass="p-7">
						<form class="flex flex-col gap-4.5" onsubmit={(e) => e.preventDefault()}>
							<div class="flex flex-col gap-1.5">
								<h3 class="text-on-white-main">Cadastrar Usuário</h3>
								<p class="text-xs leading-[150%] text-on-white-tertiary">
									Novo por aqui? Preencha seu perfil de acesso.
								</p>
							</div>

							<div class="flex flex-col gap-1.75">
								<Label>Tipo de perfil</Label>
								<RadioGroup.Root bind:value={profileType}>
									<RadioGroup.Item value="lawyer">
										<Scale class="size-3.75" />
										Advogado
									</RadioGroup.Item>
									<RadioGroup.Item value="individual">Usuário Comum</RadioGroup.Item>
								</RadioGroup.Root>
							</div>

							<TextInput
								label="Nome Completo"
								type="text"
								placeholder="Fulano da Silva"
								autocomplete="name"
								bind:value={fullName}
							/>

							<TextInput
								label="E-mail"
								type="email"
								placeholder="fulano@exemplo.com.br"
								autocomplete="email"
								bind:value={registerEmail}
							/>

							<div class="flex flex-row gap-3.5">
								<TextInput
									wrapperClass="flex-1"
									label="CPF"
									type="text"
									placeholder="123.456.789-09"
									bind:value={cpf}
								/>
								{#if profileType === 'lawyer'}
									<TextInput
										wrapperClass="flex-1"
										label="Número da OAB"
										type="text"
										placeholder="45.678 / BA"
										class="border-[#2563eb]! bg-[#eff6ff]! focus:border-[#2563eb]! focus:ring-[#2563eb]/15!"
										bind:value={oabNumber}
									/>
								{/if}
							</div>

							{#if profileType === 'lawyer'}
								<div class="flex flex-row items-center gap-1.75">
									<Info class="size-3.25 shrink-0 text-[#2563eb]" />
									<p class="text-[11px] text-[#2563eb]">
										Número da OAB obrigatório para o perfil Advogado.
									</p>
								</div>
							{/if}

							<TextInput
								label="Senha"
								type={showRegisterPassword ? 'text' : 'password'}
								placeholder="••••••••••••"
								autocomplete="new-password"
								hint="Use ao menos 8 caracteres, letras, números e símbolos."
								bind:value={registerPassword}
							>
								{#snippet trailing()}
									<Button
										type="button"
										variant="ghost"
										size="icon"
										class="text-on-white-tertiary hover:text-on-white-main"
										aria-label={showRegisterPassword ? 'Ocultar senha' : 'Mostrar senha'}
										onclick={() => (showRegisterPassword = !showRegisterPassword)}
									>
										{#if showRegisterPassword}
											<Eye class="size-4" />
										{:else}
											<EyeOff class="size-4" />
										{/if}
									</Button>
								{/snippet}
							</TextInput>

							<div class="flex flex-row items-center gap-2.25">
								<Checkbox id={termsId} bind:checked={acceptedTerms} />
								<Label for={termsId} variant="inline">
									Li e aceito os Termos de Uso e a Política de Privacidade da Veridt.
								</Label>
							</div>

							<Button type="submit" class="w-full">
								<ArrowRight class="size-4" />
								Criar Conta
							</Button>
						</form>
					</ScrollArea>
				</Tabs.Content>
			</Tabs.Root>
		</div>
		<div class="flex shrink-0 flex-row items-center justify-center gap-1.75">
			<Shield class="size-3.5 text-on-white-tertiary" />
			<p class="text-[11px] text-on-white-tertiary">
				Seus dados pessoais são tratados de acordo com a LGPD.
			</p>
		</div>
	</div>
</div>
