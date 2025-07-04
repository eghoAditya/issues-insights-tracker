// src/routes/+page.ts
import { fetchIssues } from '$lib/api';

export const load = async () => {
	const issues = await fetchIssues();
	return { issues };
};
