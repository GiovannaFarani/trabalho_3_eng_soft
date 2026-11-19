import { describe, expect, it, vi } from 'vitest';

vi.mock('$app/paths', () => ({
	resolve: (path: string) => path
}));

import { load } from './+page.ts';

function invokeLoad(urlString: string) {
	try {
		load({ url: new URL(urlString) } as Parameters<typeof load>[0]);
	} catch (thrown) {
		return thrown as { status: number; location: string };
	}
	return null;
}

describe('/reset-password route redirect', () => {
	it('redirects ?token= links from recovery emails to /login?token=', () => {
		const result = invokeLoad('http://localhost:5173/reset-password?token=abc-123');
		expect(result).toEqual({
			status: 307,
			location: '/login?token=abc-123'
		});
	});

	it('supports legacy ?resetToken= query parameter', () => {
		const result = invokeLoad('http://localhost:5173/reset-password?resetToken=legacy-456');
		expect(result).toEqual({
			status: 307,
			location: '/login?token=legacy-456'
		});
	});

	it('redirects to /login?recover=1 when no token is provided', () => {
		const result = invokeLoad('http://localhost:5173/reset-password');
		expect(result).toEqual({
			status: 307,
			location: '/login?recover=1'
		});
	});
});
