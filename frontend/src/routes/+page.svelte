<script lang="ts">
	import { onMount } from 'svelte';
	import jwt_decode from 'jwt-decode';

	type Issue = {
		id: number;
		title: string;
		description: string;
		severity: string;
		status: string;
		reporter_id: number;
		created_at: string;
	};

	let issues: Issue[] = [];
	let title = '';
	let description = '';
	let severity = 'LOW';
	let file: File | null = null;

	let error = '';
	let success = false;
	let isLoggedIn = false;
	let email = '';
	let password = '';
	let userEmail = '';
	let userRole = '';

	const logout = () => {
		localStorage.removeItem('token');
		location.reload();
	};

	const extractUserDetails = () => {
		const token = localStorage.getItem('token');
		if (!token) return;
		try {
			const decoded: any = jwt_decode(token);
			userEmail = decoded.email ?? 'User';
			userRole = decoded.role ?? 'REPORTER';
		} catch (err) {
			console.error('JWT decode failed:', err);
			userEmail = 'User';
			userRole = 'REPORTER';
		}
	};

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
		extractUserDetails();
		error = '';
		location.reload();
	};

	const fetchIssues = async () => {
		const token = localStorage.getItem('token');
		if (!token) return;

		const res = await fetch('http://localhost:8000/issues/', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (res.ok) {
			issues = await res.json();
		} else {
			console.error('❌ Failed to fetch issues');
		}
	};

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
		await fetchIssues();
	};

	const updateStatus = async (id: number, newStatus: string) => {
		const token = localStorage.getItem('token');
		const res = await fetch(`http://localhost:8000/issues/${id}`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${token}`
			},
			body: JSON.stringify(newStatus)
		});

		if (res.ok) {
			await fetchIssues();
		} else {
			console.error('❌ Failed to update status');
		}
	};

	const deleteIssue = async (id: number) => {
		const token = localStorage.getItem('token');
		const res = await fetch(`http://localhost:8000/issues/${id}`, {
			method: 'DELETE',
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (res.ok) {
			await fetchIssues();
		} else {
			console.error('❌ Failed to delete issue');
		}
	};

	onMount(() => {
		const token = localStorage.getItem('token');
		isLoggedIn = !!token;

		if (isLoggedIn) {
			extractUserDetails();
			fetchIssues();
		} else {
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
						extractUserDetails();
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
		<div id="google-signin" class="mt-4"></div>
		{#if error}
			<p class="text-red-600">{error}</p>
		{/if}
	</form>
{:else}
	<!-- User Info -->
	<div class="mb-4 flex justify-between items-center bg-gray-100 p-4 rounded border">
		<p class="text-gray-700">Logged in as <strong>{userEmail}</strong> ({userRole})</p>
		<button on:click={logout} class="bg-red-600 text-white px-4 py-1 rounded">Logout</button>
	</div>

	{#if userRole === 'REPORTER'}
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
				<input id="file" type="file" on:change={(e) => file = (e.target as HTMLInputElement).files?.[0] || null} class="border px-2 py-1 rounded w-full" />
			</div>

			<button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>

			{#if error}
				<p class="text-red-600">{error}</p>
			{/if}
			{#if success}
				<p class="text-green-600">✅ Success!</p>
			{/if}
		</form>
	{/if}

	<!-- Issue List -->
	<h1 class="text-2xl font-bold mb-4">Issues</h1>

	{#if issues.length > 0}
		<ul class="space-y-4">
			{#each issues as issue}
				<li class="p-4 rounded bg-gray-100 border border-gray-300 space-y-1">
					<h2 class="text-lg font-semibold">{issue.title}</h2>
					<p class="text-sm">{issue.description}</p>
					<p class="text-sm">Severity: {issue.severity}</p>
					<p class="text-sm">Status: 
						{#if userRole === 'MAINTAINER'}
							<select on:change={(e) => updateStatus(issue.id, `"${e.target.value}"`)} bind:value={issue.status}>
								<option value="OPEN">Open</option>
								<option value="RESOLVED">Resolved</option>
								<option value="ACTIVE">Active</option>
							</select>
						{:else}
							<strong>{issue.status}</strong>
						{/if}
					</p>
					<p class="text-xs text-gray-500">Created: {new Date(issue.created_at).toLocaleString()}</p>
					{#if userRole === 'ADMIN'}
						<button on:click={() => deleteIssue(issue.id)} class="mt-1 text-sm text-red-600 underline">Delete</button>
					{/if}
				</li>
			{/each}
		</ul>
	{:else}
		<p>No issues found.</p>
	{/if}
{/if}
