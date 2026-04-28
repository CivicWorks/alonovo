import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		allowedHosts: ['alonovo.cooperation.org', 'alonovo.linkedtrust.us', 'demos.linkedtrust.us'],
		proxy: {
			'/alonovo/api': {
				target: 'http://127.0.0.1:8020',
				changeOrigin: true,
			},
		},
		hmr: {
			// Use the nginx proxy so the browser doesn't prompt about local network
			clientPort: 443,
			protocol: 'wss',
		},
	}
});
