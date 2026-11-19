import { resolve } from '$app/paths';
import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
	const token = url.searchParams.get('token')?.trim() || url.searchParams.get('resetToken')?.trim();

	const params = new URLSearchParams();
	if (token) {
		params.set('token', token);
	} else {
		params.set('recover', '1');
	}

	redirect(307, `${resolve('/login')}?${params.toString()}`);
};
