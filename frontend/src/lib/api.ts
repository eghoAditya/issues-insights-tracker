// src/lib/api.ts
export async function fetchIssues() {
	const res = await fetch('http://localhost:8000/issues/', {
		headers: {
			Authorization: 'Bearer YOUR_TOKEN_HERE'  // we'll skip auth for now or disable auth temporarily
		}
	});
	if (!res.ok) throw new Error('Failed to fetch issues');
	return res.json();
}
