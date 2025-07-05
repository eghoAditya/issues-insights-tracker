<script lang="ts">
    import { onMount } from 'svelte';
  
    let token = '';
  
    onMount(() => {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  
      if (!window.google || !window.google.accounts) return;
  
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response: any) => {
          const res = await fetch('http://localhost:8000/api/login/google', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: response.credential })
          });
  
          const data = await res.json();
          token = data.access_token;
          localStorage.setItem('token', token);
          console.log('Logged in with Google! Token:', token);
        }
      });
  
      window.google.accounts.id.prompt();
    });
  </script>
  
  <slot />
  