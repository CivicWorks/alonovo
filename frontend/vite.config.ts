import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		allowedHosts: ['alonovo.cooperation.org', 'alonovo.linkedtrust.us', 'demos.linkedtrust.us'],
		hmr: false,
	}
});
