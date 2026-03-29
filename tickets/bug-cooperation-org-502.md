# Bug: alonovo.cooperation.org returns 502

## Where
https://alonovo.cooperation.org — all pages

## What
The domain returns HTTP 502 (Bad Gateway). The Caddy config routes `alonovo.cooperation.org` to `10.0.0.106:80` (VM 106), but that VM is not responding. The app actually runs on VM 200 (this VM) and is only accessible via `demos.linkedtrust.us/alonovo/`.

## Expected
Both domains should load the site.

## Steps to Reproduce
1. Open https://alonovo.cooperation.org in a browser
2. See blank page / 502 error

## Notes
- `caddy-domain list` shows: `alonovo.cooperation.org -> 10.0.0.106:80`
- The actual services run on VM 200: `tmp-alonovo-backend.service` (port 8020) and `tmp-alonovo-frontend.service` (port 3020)
- `demos.linkedtrust.us/alonovo/` works fine
- Either the Caddy route needs to point to VM 200, or VM 106 needs the app running
