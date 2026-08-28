<script lang="ts">
    let { url, title }: { url: string; title: string } = $props();
    let copied = $state(false);

    function shareBluesky() {
        window.open(`https://bsky.app/intent/compose?text=${encodeURIComponent(`${title} ${url}`)}`, '_blank');
    }

    function shareLinkedIn() {
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
    }

    function shareFacebook() {
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
    }

    async function copyLink() {
        try {
            await navigator.clipboard.writeText(url);
            copied = true;
            setTimeout(() => copied = false, 2000);
        } catch {
            // Fallback for older browsers
            const input = document.createElement('input');
            input.value = url;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            copied = true;
            setTimeout(() => copied = false, 2000);
        }
    }
</script>

<div class="share-buttons">
    <span class="share-label">Share</span>
    <button class="share-btn" onclick={shareBluesky} title="Share on Bluesky">
        <svg viewBox="0 0 568 501" width="18" height="18" fill="currentColor">
            <path d="M123.121 33.664C188.241 82.553 258.281 181.68 284 234.873c25.719-53.192 95.759-152.32 160.879-201.21C491.866-1.611 568-28.906 568 57.947c0 17.346-9.945 145.713-15.778 166.555-20.275 72.453-94.155 90.933-159.875 79.748C507.222 323.8 536.444 388.56 473.333 453.32c-119.86 122.992-172.272-30.859-185.702-70.281-2.462-7.227-3.614-10.608-3.631-7.733-.017-2.875-1.169.506-3.631 7.733-13.43 39.422-65.842 193.273-185.702 70.281-63.111-64.76-33.89-129.52 80.986-149.071-65.72 11.185-139.6-7.295-159.875-79.748C9.945 203.66 0 75.293 0 57.947 0-28.906 76.135-1.611 123.121 33.664Z"/>
        </svg>
    </button>
    <button class="share-btn" onclick={shareLinkedIn} title="Share on LinkedIn">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
    </button>
    <button class="share-btn" onclick={shareFacebook} title="Share on Facebook">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
    </button>
    <button class="share-btn" onclick={copyLink} title="Copy link">
        {#if copied}
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
        {:else}
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
            </svg>
        {/if}
    </button>
</div>

<style>
    .share-buttons {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
    }

    .share-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    .share-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border: 1px solid var(--border-color);
        border-radius: 0.25rem;
        background: transparent;
        color: var(--text-muted);
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s, background-color 0.15s;
    }

    .share-btn:hover {
        border-color: var(--accent);
        color: var(--accent);
        background: rgba(45, 212, 191, 0.1);
    }
</style>
