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
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import {
		ApiError,
		authSession,
		Button,
		Checkbox,
		isStrongPassword,
		Label,
		PASSWORD_RULE_MESSAGE,
		passwordRecoveryClient,
		RadioGroup,
		ScrollArea,
		Tabs,
		TextInput
	} from '#lib';

	let email = $state('');
	let password = $state('');
	let showPassword = $state(false);
	let isRecoveringPassword = $state(false);
	let recoveryStep = $state<'request' | 'confirm' | 'done'>('request');
	let recoveryEmail = $state('');
	let resetToken = $state('');
	let newPassword = $state('');
	let showNewPassword = $state(false);
	let isSubmittingRecovery = $state(false);
	let recoveryError = $state<string | null>(null);
	let tokenError = $state<string | null>(null);
	let newPasswordError = $state<string | null>(null);
	let recoveryMessage = $state<string | null>(null);

	let profileType = $state<'lawyer' | 'individual'>('lawyer');
	let fullName = $state('');
	let registerEmail = $state('');
	let cpf = $state('');
	let oabNumber = $state('');
	let registerPassword = $state('');
	let showRegisterPassword = $state(false);
	let acceptedTerms = $state(false);

	const termsId = $props.id();

	$effect(() => {
		const tokenFromUrl =
			page.url.searchParams.get('token')?.trim() || page.url.searchParams.get('resetToken')?.trim();
		const isRecoveryUrl = Boolean(tokenFromUrl) || page.url.searchParams.get('recover') === '1';

		if (tokenFromUrl) {
			isRecoveringPassword = true;
			recoveryStep = 'confirm';
			resetToken = tokenFromUrl;
		} else if (page.url.searchParams.get('recover') === '1') {
			isRecoveringPassword = true;
			recoveryStep = 'confirm';
		} else if (authSession.isAuthenticated && !isRecoveringPassword && !isRecoveryUrl) {
			void goto(resolve('/(workspace)/records'), { replaceState: true });
		}
	});

	function clearRecoveryFeedback() {
		recoveryError = null;
		tokenError = null;
		newPasswordError = null;
		recoveryMessage = null;
	}

	function resetRecoveryFlow() {
		isRecoveringPassword = false;
		recoveryStep = 'request';
		clearRecoveryFeedback();
	}

	async function handleRequestRecovery(event: SubmitEvent) {
		event.preventDefault();
		recoveryError = null;
		recoveryMessage = null;

		const trimmedEmail = recoveryEmail.trim();
		if (!trimmedEmail) {
			recoveryError = 'Informe o e-mail de recuperação.';
			return;
		}

		isSubmittingRecovery = true;
		try {
			const response = await passwordRecoveryClient.requestPasswordReset({
				email: trimmedEmail
			});
			recoveryMessage = response.data.message;
			recoveryStep = 'confirm';
		} catch (error) {
			recoveryError =
				error instanceof ApiError
					? error.message
					: 'Não foi possível solicitar a recuperação de senha.';
		} finally {
			isSubmittingRecovery = false;
		}
	}

	async function handleConfirmReset(event: SubmitEvent) {
		event.preventDefault();
		clearRecoveryFeedback();

		const trimmedToken = resetToken.trim();
		if (!trimmedToken) {
			tokenError = 'Informe o token recebido por e-mail.';
			return;
		}

		if (!isStrongPassword(newPassword)) {
			newPasswordError = PASSWORD_RULE_MESSAGE;
			return;
		}

		isSubmittingRecovery = true;
		try {
			const response = await passwordRecoveryClient.confirmPasswordReset({
				token: trimmedToken,
				nova_senha: newPassword
			});
			recoveryMessage = response.data.message;
			recoveryStep = 'done';
			resetToken = '';
			newPassword = '';
		} catch (error) {
			const message =
				error instanceof ApiError ? error.message : 'Não foi possível redefinir a senha.';
			if (message.toLowerCase().includes('senha')) {
				newPasswordError = message;
			} else {
				tokenError = message;
			}
		} finally {
			isSubmittingRecovery = false;
		}
	}
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
			<div class="flex flex-row items-center gap-2">
				<div class="h-0.5 w-6 shrink-0 bg-on-veridt-blue-muted"></div>
				<p class="text-[11px] text-on-veridt-blue">EVIDÊNCIA. INTEGRIDADE. CONFIANÇA.</p>
			</div>
			<h1 class="text-white">
				Provas Digitais com Validade Jurídica e Imutabilidade WORM - SHA-256
			</h1>
			<p class="text-sm leading-[170%] text-on-veridt-blue">
				Da captura à preservação, uma cadeia de custódia digital rastreável para advogados e pessoas
				físicas.
			</p>
			<div class="flex flex-row justify-between py-6.25">
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-veridt-blue-border bg-veridt-blue-surface"
				>
					<ScanLine class="size-8.75 text-on-veridt-blue" />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-veridt-blue-border bg-veridt-blue-surface"
				>
					<FingerprintPattern class="size-8.75 text-on-veridt-blue" />
				</div>
				<div
					class="size-20 content-center justify-items-center rounded-2xl border border-veridt-blue-border bg-veridt-blue-surface"
				>
					<ShieldCheck class="size-8.75 text-shield-green" />
				</div>
			</div>
			<div class="flex flex-row items-center gap-2">
				<LockKeyhole class="size-4.5 text-shield-green" />
				<p class="text-xs text-shield-green-light">
					Preservação imutável. Verificação independente.
				</p>
			</div>
		</div>
		<div class="flex flex-col gap-3">
			<p class="text-[11px] text-on-veridt-blue-muted">© 2026 Veridt</p>
			<div class="flex flex-row items-center gap-2 text-[11px] text-on-veridt-blue">
				<button
					type="button"
					class="cursor-pointer underline-offset-4 transition-colors hover:text-white hover:underline"
				>
					Termos de uso
				</button>
				<span aria-hidden="true">•</span>
				<button
					type="button"
					class="cursor-pointer underline-offset-4 transition-colors hover:text-white hover:underline"
				>
					Política de privacidade
				</button>
			</div>
		</div>
	</div>
	<div class="flex h-full min-w-0 flex-1 flex-col gap-7 overflow-hidden px-11 pt-13 pb-8">
		<div class="flex shrink-0 flex-col">
			<div class="flex flex-row justify-between">
				<p class="text-[11px] text-on-white-tertiary">ACESSO À PLATAFORMA</p>
				<button
					type="button"
					class="flex cursor-pointer flex-row items-center gap-1.5 text-xs text-on-white-secondary underline-offset-4 transition-colors hover:text-on-white-main hover:underline"
				>
					<CircleQuestionMark class="size-4" />
					<span>Precisa de ajuda?</span>
				</button>
			</div>
			<h2 class="text-on-white-main">Sua evidência começa aqui.</h2>
			<p class="text-sm text-on-white-secondary">
				Entre na sua conta ou crie um perfil para iniciar seus registros.
			</p>
		</div>
		<div
			class="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-card-border bg-white"
		>
			<Tabs.Root
				value="login"
				class="min-h-0 flex-1"
				onValueChange={(value) => {
					if (value !== 'login') resetRecoveryFlow();
				}}
			>
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
							{#if recoveryStep === 'request'}
								<form
									class="flex flex-col gap-4 rounded-xl border border-card-border bg-surface-subtle p-5"
									onsubmit={handleRequestRecovery}
								>
									<div class="flex flex-row items-center gap-2.25">
										<KeyRound class="size-4.5 text-on-white-main" />
										<p class="text-[15px] text-on-white-main">Recuperar Senha</p>
									</div>
									<p class="text-xs leading-[160%] text-on-white-secondary">
										Informe o e-mail da sua conta. Enviaremos um link e um token para definir uma
										nova senha.
									</p>
									<TextInput
										label="E-mail de recuperação"
										type="email"
										placeholder="fulano@exemplo.com.br"
										autocomplete="email"
										hint="&nbsp;"
										error={recoveryError ?? undefined}
										disabled={isSubmittingRecovery}
										bind:value={recoveryEmail}
									/>
									<Button
										type="submit"
										variant="outline"
										class="w-full"
										disabled={isSubmittingRecovery}
									>
										<Mail class="size-4" />
										{isSubmittingRecovery ? 'Enviando...' : 'Enviar link de recuperação'}
									</Button>
									<div class="flex flex-row items-center justify-between gap-2">
										<Button
											type="button"
											variant="link"
											size="sm"
											class="text-[11px]! font-normal! text-on-white-tertiary! hover:text-on-white-main!"
											onclick={resetRecoveryFlow}
										>
											Voltar para Entrar
										</Button>
										<Button
											type="button"
											variant="link"
											size="sm"
											class="text-[11px]! font-normal! text-on-white-secondary! hover:text-on-white-main!"
											onclick={() => {
												clearRecoveryFeedback();
												recoveryStep = 'confirm';
											}}
										>
											Já tenho um token
										</Button>
									</div>
								</form>
							{:else if recoveryStep === 'confirm'}
								<form
									class="flex flex-col gap-4 rounded-xl border border-card-border bg-surface-subtle p-5"
									onsubmit={handleConfirmReset}
								>
									<div class="flex flex-row items-center gap-2.25">
										<KeyRound class="size-4.5 text-on-white-main" />
										<p class="text-[15px] text-on-white-main">Redefinir Senha</p>
									</div>
									{#if recoveryMessage}
										<p role="status" class="text-xs leading-[160%] text-emerald-700">
											{recoveryMessage}
										</p>
									{:else}
										<p class="text-xs leading-[160%] text-on-white-secondary">
											Informe o token recebido por e-mail e defina sua nova senha.
										</p>
									{/if}
									<TextInput
										label="Token recebido por e-mail"
										type="text"
										placeholder="Cole o token de recuperação"
										autocomplete="one-time-code"
										hint="&nbsp;"
										error={tokenError ?? undefined}
										disabled={isSubmittingRecovery}
										bind:value={resetToken}
									/>
									<TextInput
										label="Nova Senha"
										type={showNewPassword ? 'text' : 'password'}
										placeholder="••••••••••••"
										autocomplete="new-password"
										hint="Use ao menos 8 caracteres, letras, números e símbolos (@$!%*#?&)."
										error={newPasswordError ?? undefined}
										disabled={isSubmittingRecovery}
										bind:value={newPassword}
									>
										{#snippet trailing()}
											<Button
												type="button"
												variant="ghost"
												size="icon"
												class="text-on-white-tertiary hover:text-on-white-main"
												aria-label={showNewPassword ? 'Ocultar senha' : 'Mostrar senha'}
												onclick={() => (showNewPassword = !showNewPassword)}
											>
												{#if showNewPassword}
													<Eye class="size-4" />
												{:else}
													<EyeOff class="size-4" />
												{/if}
											</Button>
										{/snippet}
									</TextInput>
									<Button type="submit" class="w-full" disabled={isSubmittingRecovery}>
										<ArrowRight class="size-4" />
										{isSubmittingRecovery ? 'Redefinindo...' : 'Redefinir senha'}
									</Button>
									<div class="flex flex-row items-center justify-between gap-2">
										<Button
											type="button"
											variant="link"
											size="sm"
											class="text-[11px]! font-normal! text-on-white-tertiary! hover:text-on-white-main!"
											onclick={resetRecoveryFlow}
										>
											Voltar para Entrar
										</Button>
										<Button
											type="button"
											variant="link"
											size="sm"
											class="text-[11px]! font-normal! text-on-white-secondary! hover:text-on-white-main!"
											onclick={() => {
												clearRecoveryFeedback();
												recoveryStep = 'request';
											}}
										>
											Solicitar novo token
										</Button>
									</div>
								</form>
							{:else}
								<div
									class="flex flex-col gap-4 rounded-xl border border-card-border bg-surface-subtle p-5"
								>
									<div class="flex flex-row items-center gap-2.25">
										<ShieldCheck class="size-4.5 text-shield-green" />
										<p class="text-[15px] text-on-white-main">Senha Redefinida</p>
									</div>
									<p
										role="status"
										class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-800"
									>
										{recoveryMessage ?? 'Senha redefinida com sucesso.'}
									</p>
									<Button type="button" class="w-full" onclick={resetRecoveryFlow}>
										<ArrowRight class="size-4" />
										Voltar para Entrar
									</Button>
								</div>
							{/if}
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
										class="border-status-processing! bg-status-processing-bg! focus:border-status-processing! focus:ring-status-processing/15!"
										bind:value={oabNumber}
									/>
								{/if}
							</div>

							{#if profileType === 'lawyer'}
								<div class="flex flex-row items-center gap-1.75">
									<Info class="size-3.25 shrink-0 text-status-processing" />
									<p class="text-[11px] text-status-processing">
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
									Li e aceito os
									<button
										type="button"
										class="inline cursor-pointer font-semibold text-on-white-main underline-offset-4 hover:underline"
										onclick={(e) => e.stopPropagation()}
									>
										Termos de Uso
									</button>
									e a
									<button
										type="button"
										class="inline cursor-pointer font-semibold text-on-white-main underline-offset-4 hover:underline"
										onclick={(e) => e.stopPropagation()}
									>
										Política de Privacidade
									</button>
									da Veridt.
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
