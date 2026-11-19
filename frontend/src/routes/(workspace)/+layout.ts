import { resolve } from '$app/paths';
import { redirect } from '@sveltejs/kit';
import { authSession } from '#lib';
import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = () => {
	if (!authSession.getAuthToken()) {
		redirect(307, resolve('/login'));
	}
};
