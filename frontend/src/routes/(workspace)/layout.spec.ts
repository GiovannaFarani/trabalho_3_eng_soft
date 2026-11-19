import { beforeEach, describe, expect, it, vi } from 'vitest';

const getAuthTokenMock = vi.fn<() => string | null>();

vi.mock('$app/paths', () => ({
	resolve: (path: string) => path
}));

vi.mock('#lib', () => ({
	authSession: {
		getAuthToken: () => getAuthTokenMock()
	}
}));

import { load, ssr } from './+layout.ts';

describe('(workspace) layout auth guard', () => {
	beforeEach(() => {
		getAuthTokenMock.mockReset();
	});

	it('disables SSR so unauthenticated HTML is never rendered on the server', () => {
		expect(ssr).toBe(false);
	});

	it('redirects to /login before mounting when unauthenticated', () => {
		getAuthTokenMock.mockReturnValue(null);

		let thrown: unknown = null;
		try {
			load({} as Parameters<typeof load>[0]);
		} catch (error) {
			thrown = error;
		}

		expect(thrown).toEqual({
			status: 307,
			location: '/login'
		});
	});

	it('allows navigation when a valid auth token exists', () => {
		getAuthTokenMock.mockReturnValue('valid-jwt-token');

		expect(() => load({} as Parameters<typeof load>[0])).not.toThrow();
	});
});
