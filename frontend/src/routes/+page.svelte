<script lang="ts">
	type Issue = {
		id: number;
		title: string;
		description: string;
		created_at: string;
	};

	export let data: { issues: Issue[] };
</script>

<h1 class="text-2xl font-bold mb-4">Issues</h1>

{#if data.issues.length > 0}
	<ul class="space-y-2">
		{#each data.issues as issue}
			<li class="p-4 rounded bg-gray-100 border border-gray-300">
				<h2 class="text-lg font-semibold">{issue.title}</h2>
				<p class="text-sm text-gray-700">{issue.description}</p>
				<p class="text-xs text-gray-500 mt-1">Created at: {new Date(issue.created_at).toLocaleString()}</p>
			</li>
		{/each}
	</ul>
{:else}
	<p>No issues found.</p>
{/if}
