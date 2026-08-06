# Bug: About page returns 404 on alonovo.linkedtrust.us

## Where
https://alonovo.linkedtrust.us/about

## What
The about page returns HTTP 404. The file `about.html` exists in the build directory, and the route exists in the Svelte source (`src/routes/about/+page.svelte`), but the alonovo.linkedtrust.us domain doesn't serve it. However, `demos.linkedtrust.us/alonovo/about` likely works since it uses the nginx config with `try_files`.

## Expected
The about page should load and show data source information.

## Steps to Reproduce
1. Go to https://alonovo.linkedtrust.us/about
2. See 404 error

## Notes
The alonovo.linkedtrust.us domain routing may not have the SvelteKit fallback configured properly. The demos.linkedtrust.us/alonovo/ nginx config has `try_files $uri $uri/ /alonovo/index.html` which handles SPA routing.
