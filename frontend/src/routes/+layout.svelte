<script lang="ts">
	import { onMount } from 'svelte';
  
	onMount(() => {
	  const token = localStorage.getItem("token");
	  if (token) return;
  
	  const script = document.createElement("script");
	  script.src = "https://accounts.google.com/gsi/client";
	  script.async = true;
	  script.defer = true;
  
	  script.onload = () => {
		// @ts-ignore
		if (!window.google?.accounts?.id) {
		  console.error("Google SDK not loaded properly");
		  return;
		}
  
		// @ts-ignore
		window.google.accounts.id.initialize({
		  client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
		  callback: async (response: any) => {
			try {
			  const res = await fetch("http://localhost:8000/login/google", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ token: response.credential }),
			  });
  
			  if (res.ok) {
				const data = await res.json();
				localStorage.setItem("token", data.access_token);
				window.location.reload();
			  } else {
				console.error("Google login failed", await res.text());
			  }
			} catch (err) {
			  console.error("Error during Google login", err);
			}
		  },
		});
  
		// @ts-ignore
		window.google.accounts.id.prompt();
	  };
  
	  document.head.appendChild(script);
	});
  </script>
  
  <slot />
  