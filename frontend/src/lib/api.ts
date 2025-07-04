// src/lib/api.ts

export async function fetchIssues() {
	const res = await fetch('http://localhost:8000/issues/');
	if (!res.ok) {
		throw new Error('Failed to fetch issues');
	}
	return await res.json();
}
