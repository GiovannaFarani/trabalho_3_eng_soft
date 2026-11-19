// place files you want to import through the `#lib` alias in this folder.
export { Tabs, TabsRoot, TabsList, TabsTrigger, TabsContent } from './components/tabs/index.ts';
export {
	Button,
	type ButtonProps,
	type ButtonSize,
	type ButtonVariant
} from './components/button/index.ts';
export { Checkbox, type CheckboxProps } from './components/checkbox/index.ts';
export { Label, type LabelProps, type LabelVariant } from './components/label/index.ts';
export { RadioGroup, RadioGroupRoot, RadioGroupItem } from './components/radio-group/index.ts';
export {
	ScrollArea,
	type ScrollAreaOrientation,
	type ScrollAreaProps
} from './components/scroll-area/index.ts';
export {
	TextInput,
	Input,
	type TextInputProps,
	type TextInputType
} from './components/input/index.ts';
export {
	ApiError,
	CORRELATION_ID_HEADER,
	createHttpClient,
	type ApiResponse,
	type HttpClient,
	type HttpClientConfig,
	type HttpGetClient,
	type HttpPostClient,
	type RequestOptions
} from './api/httpClient.ts';
export {
	authLoginClient,
	authLogoutClient,
	authRegisterClient,
	coreAuthHttpClient,
	createAuthLoginClient,
	createAuthLogoutClient,
	createAuthRegisterClient,
	createPasswordRecoveryClient,
	isStrongPassword,
	normalizeBackendUser,
	PASSWORD_RULE_MESSAGE,
	passwordRecoveryClient,
	STRONG_PASSWORD_REGEX,
	TERMS_REQUIRED_MESSAGE,
	type AuthLoginClient,
	type AuthLogoutClient,
	type AuthRegisterClient,
	type BackendUserDto,
	type ForgotPasswordRequest,
	type LoginRequest,
	type LoginResponseDto,
	type LoginResult,
	type MessageResponse,
	type PasswordRecoveryClient,
	type ProfileTypeDto,
	type RegisterRequest,
	type RegisterResponse,
	type ResetPasswordRequest
} from './api/coreAuthClient.ts';
export {
	createRecordsReaderClient,
	evidenceHttpClient,
	formatRecordTimestamp,
	mapEvidenceRecordDto,
	mapRecordStatus,
	recordsReaderClient,
	splitDetailsSummary,
	type BackendRecordStatus,
	type EvidenceRecord,
	type EvidenceRecordDto,
	type EvidenceRecordStatus,
	type RecordsReaderClient
} from './api/evidenceRecordsClient.ts';
export {
	AUTH_TOKEN_STORAGE_KEY,
	AUTH_USER_STORAGE_KEY,
	authSession,
	createAuthSessionStore,
	decodeJwtUser,
	formatUserDisplayLabel,
	formatUserInitials,
	isTokenExpired,
	type AuthenticatedUser,
	type AuthSessionReader,
	type AuthSessionStore,
	type AuthSessionStoreConfig,
	type AuthSessionWriter,
	type KeyValueStorage,
	type TokenProvider,
	type UserRole
} from './auth/session.svelte.ts';
