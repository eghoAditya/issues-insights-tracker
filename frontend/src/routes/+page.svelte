<script lang="ts">
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

	const handleSubmit = async (e: SubmitEvent) => {
	e.preventDefault();
	error = '';
	success = false;

	const formData = new FormData();
	formData.append('title', title);
	formData.append('description', description);
	formData.append('severity', severity);
	if (file) {
		formData.append('file', file);
	}

	const token = localStorage.getItem('token');

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
	location.reload(); // Reload the issue list
};

</script>

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
			class="border px-2 py-1 rounded w-full"
			on:change={(e) => {
				const target = e.target as HTMLInputElement;
				file = target.files?.[0] || null;
			}} />
	</div>
	

	<button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>

	{#if error}
		<p class="text-red-600">{error}</p>
	{/if}
	{#if success}
		<p class="text-green-600">Issue created successfully!</p>
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
