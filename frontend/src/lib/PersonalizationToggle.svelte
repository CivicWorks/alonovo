<script lang="ts">
    import { getUser, isPersonalized, setPersonalized, getPersonalizedRaw } from '$lib/stores.svelte';

    const user = $derived(getUser());
    const active = $derived(getPersonalizedRaw());

    function toggle() {
        setPersonalized(!active);
    }
</script>

{#if user}
    <label class="personalize-toggle">
        <span class="toggle-label" class:active={active}>Personalized Scores</span>
        <span class="toggle-track" class:active={active} onclick={toggle} role="switch" aria-checked={active}>
            <span class="toggle-thumb"></span>
        </span>
    </label>
{/if}

<style>
    .personalize-toggle {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        white-space: nowrap;
    }

    .toggle-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    .toggle-label.active {
        color: var(--accent);
        font-weight: 600;
    }

    .toggle-track {
        position: relative;
        width: 32px;
        height: 18px;
        background: var(--color-surface-700);
        border-radius: 9px;
        cursor: pointer;
        transition: background-color 0.15s;
    }

    .toggle-track.active {
        background: var(--color-brand-600);
    }

    .toggle-thumb {
        position: absolute;
        top: 2px;
        left: 2px;
        width: 14px;
        height: 14px;
        background: var(--text-muted);
        border-radius: 50%;
        transition: left 0.15s, background-color 0.15s;
    }

    .toggle-track.active .toggle-thumb {
        left: 16px;
        background: var(--text-primary);
    }
</style>
