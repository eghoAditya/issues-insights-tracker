<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
  
	let chart: any;
	let userEmail = '';
  
	onMount(async () => {
	  if (!browser) return;
  
	  const token = localStorage.getItem('access_token');
	  userEmail = localStorage.getItem('user_email') || '';
  
	  try {
		const res = await fetch('http://localhost:8000/insights/', {
		  headers: {
			Authorization: `Bearer ${token}`
		  }
		});
		const chartData = await res.json();
  
		console.log('📊 Chart data:', chartData);
  
		// Ensure chartData is an array
		if (!Array.isArray(chartData)) {
		  throw new Error('Chart data is not an array');
		}
  
		const labels = chartData.map(item => item.severity);
		const counts = chartData.map(item => item.count);
  
		console.log('Labels:', labels);
		console.log('Counts:', counts);
  
		// Wait for Chart.js to be available
		const waitForChartJS = () =>
		  new Promise<void>((resolve) => {
			const check = () => {
			  if (window.Chart) resolve();
			  else setTimeout(check, 100);
			};
			check();
		  });
  
		await waitForChartJS();
  
		const ctx = document.getElementById('severityChart') as HTMLCanvasElement;
		if (ctx) {
		  chart = new Chart(ctx, {
			type: 'bar',
			data: {
			  labels: labels,
			  datasets: [{
				label: 'Issue Count by Severity',
				data: counts,
				backgroundColor: [
				  'rgba(255, 99, 132, 0.5)',
				  'rgba(255, 206, 86, 0.5)',
				  'rgba(54, 162, 235, 0.5)'
				],
				borderColor: [
				  'rgba(255, 99, 132, 1)',
				  'rgba(255, 206, 86, 1)',
				  'rgba(54, 162, 235, 1)'
				],
				borderWidth: 1
			  }]
			},
			options: {
			  responsive: true,
			  maintainAspectRatio: false,
			  scales: {
				y: {
				  beginAtZero: true
				}
			  }
			}
		  });
		}
	  } catch (err) {
		console.error('Failed to fetch chart data', err);
	  }
	});
  </script>
  
  <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
  <p class="mb-6">Welcome, {userEmail}!</p>
  
  <!-- Canvas must have height or else will appear invisible -->
  <div class="w-full h-64 relative">
	<canvas id="severityChart" class="absolute inset-0"></canvas>
  </div>
  
  <!-- Load Chart.js via CDN -->
  <svelte:head>
	<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  </svelte:head>
  