<script lang="ts">
	import { onMount } from 'svelte';

	// ✅ TypeScript support for Google
	declare global {
		interface Window {
			google?: {
				accounts: {
					id: {
						initialize: (options: any) => void;
						renderButton: (parent: HTMLElement, options: any) => void;
						prompt: () => void;
					};
				};
			};
		}
	}
	export {};

	type Issue = {
		id: number;
		title: string;
		description: string;
		severity: string;
		status: string;
		reporter_id: number;
		created_at: string;
	};

	export let data: { issues: Issue[] };

	let title = '';
	let description = '';
	let severity = 'LOW';
	let file: File | null = null;

	let error = '';
	let success = false;
	let isLoggedIn = false;
	let email = '';
	let password = '';

	// --- Email/Password Login ---
	const handleLogin = async () => {
		const res = await fetch('http://localhost:8000/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams({ username: email, password })
		});

		if (!res.ok) {
			error = '❌ Invalid email or password';
			return;
		}

		const data = await res.json();
		localStorage.setItem('token', data.access_token);
		isLoggedIn = true;
		error = '';
		location.reload();
	};

	// --- Google OAuth ---
	onMount(() => {
		const token = localStorage.getItem('token');
		isLoggedIn = !!token;

		if (!isLoggedIn) {
			const script = document.createElement('script');
			script.src = 'https://accounts.google.com/gsi/client';
			script.async = true;
			script.defer = true;
			script.onload = () => {
				window.google?.accounts.id.initialize({
					client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
					callback: async (response: any) => {
						const res = await fetch('http://localhost:8000/login/google', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({ token: response.credential })
						});

						if (!res.ok) {
							error = '❌ Google login failed';
							return;
						}

						const data = await res.json();
						localStorage.setItem('token', data.access_token);
						isLoggedIn = true;
						location.reload();
					}
				});

				window.google?.accounts.id.renderButton(
					document.getElementById('google-signin')!,
					{ theme: 'outline', size: 'large' }
				);
			};
			document.head.appendChild(script);
		}
	});

	// --- Submit New Issue ---
	const handleSubmit = async (e: SubmitEvent) => {
		e.preventDefault();
		error = '';
		success = false;

		const token = localStorage.getItem('token');
		if (!token) {
			error = 'Please login first';
			return;
		}

		const formData = new FormData();
		formData.append('title', title);
		formData.append('description', description);
		formData.append('severity', severity);
		if (file) {
			formData.append('file', file);
		}

		const res = await fetch('http://localhost:8000/issues/', {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: formData
		});

		if (!res.ok) {
			error = '❌ Failed to create issue';
			return;
		}

		success = true;
		title = '';
		description = '';
		severity = 'LOW';
		file = null;
		location.reload();
	};
</script>

{#if !isLoggedIn}
	<!-- Login Form -->
	<form on:submit|preventDefault={handleLogin} class="mb-6 space-y-4 p-4 border rounded bg-white shadow">
		<h2 class="text-xl font-semibold">Login</h2>

		<div>
			<label class="block font-medium" for="email">Email</label>
			<input id="email" bind:value={email} required class="border px-2 py-1 rounded w-full" />
		</div>

		<div>
			<label class="block font-medium" for="password">Password</label>
			<input id="password" type="password" bind:value={password} required class="border px-2 py-1 rounded w-full" />
		</div>

		<button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Login</button>

		<!-- Google Login Button -->
		<div id="google-signin" class="mt-4"></div>

		{#if error}
			<p class="text-red-600">{error}</p>
		{/if}
	</form>
{:else}
	<!-- Create Issue Form -->
	<form on:submit={handleSubmit} class="space-y-4 mb-6 p-4 border rounded bg-white shadow">
		<h2 class="text-xl font-semibold">Create New Issue</h2>

		<div>
			<label class="block font-medium" for="title">Title</label>
			<input id="title" bind:value={title} required class="border px-2 py-1 rounded w-full" />
		</div>

		<div>
			<label class="block font-medium" for="description">Description</label>
			<textarea id="description" bind:value={description} required class="border px-2 py-1 rounded w-full"></textarea>
		</div>

		<div>
			<label class="block font-medium" for="severity">Severity</label>
			<select id="severity" bind:value={severity} class="border px-2 py-1 rounded w-full">
				<option value="LOW">Low</option>
				<option value="MEDIUM">Medium</option>
				<option value="HIGH">High</option>
			</select>
		</div>

		<div>
			<label class="block font-medium" for="file">Attach File</label>
			<input
				id="file"
				type="file"
				on:change={(e: Event) =>
					(file = (e.target as HTMLInputElement).files?.[0] || null)
				}
				class="border px-2 py-1 rounded w-full"
			/>
		</div>

		<button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>

		{#if error}
			<p class="text-red-600">{error}</p>
		{/if}
		{#if success}
			<p class="text-green-600">✅ Success!</p>
		{/if}
	</form>

	<!-- Issues List -->
	<h1 class="text-2xl font-bold mb-4">Issues</h1>

	{#if data.issues.length > 0}
		<ul class="space-y-2">
			{#each data.issues as issue}
				<li class="p-4 rounded bg-gray-100 border border-gray-300">
					<h2 class="text-lg font-semibold">{issue.title}</h2>
					<p class="text-sm text-gray-700">{issue.description}</p>
					<p class="text-sm text-yellow-800">Severity: {issue.severity}</p>
					<p class="text-xs text-gray-500 mt-1">Created at: {new Date(issue.created_at).toLocaleString()}</p>
				</li>
			{/each}
		</ul>
	{:else}
		<p>No issues found.</p>
	{/if}
{/if}
