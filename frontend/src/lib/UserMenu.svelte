<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { getLoginUrl, getLogoutUrl } from '$lib/api';
    import { loadUser, getUser } from '$lib/stores.svelte';
    import type { User } from '$lib/types';

    const user = $derived(getUser());
    let menuOpen = $state(false);

    onMount(async () => {
        await loadUser();
    });

    function toggleMenu() {
        menuOpen = !menuOpen;
    }

    function closeMenu() {
        menuOpen = false;
    }

    function getInitial(user: User): string {
        return (user.email?.[0] || user.username?.[0] || '?').toUpperCase();
    }
</script>

<svelte:window on:click={closeMenu} />

<div class="user-menu">
    {#if user}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="avatar" on:click|stopPropagation={toggleMenu} title={user.email}>
            {getInitial(user)}
        </div>
        {#if menuOpen}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="dropdown" on:click|stopPropagation>
                <div class="dropdown-header">{user.email}</div>
                <a href="{base}/profile" class="dropdown-item">Profile</a>
                {#if user.is_staff}
                    <a href="{base}/admin/" class="dropdown-item">Admin</a>
                {/if}
                <a href={getLogoutUrl()} class="dropdown-item">Logout</a>
            </div>
        {/if}
    {:else}
        <a href={getLoginUrl()} class="sign-in">Sign in</a>
    {/if}
</div>

<style>
    .user-menu {
        position: relative;
    }

    .sign-in {
        color: var(--accent);
        text-decoration: none;
        font-size: 0.875rem;
        padding: 0.4rem 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: 0.25rem;
        transition: border-color 0.15s, background-color 0.15s;
    }

    .sign-in:hover {
        border-color: var(--accent);
        background: rgba(45, 212, 191, 0.1);
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--color-surface-700);
        color: var(--text-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        cursor: pointer;
        transition: background-color 0.15s;
    }

    .avatar:hover {
        background: var(--color-surface-600);
    }

    .dropdown {
        position: absolute;
        top: 44px;
        right: 0;
        background: var(--color-surface-800);
        border: 1px solid var(--border-color);
        border-radius: 0.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        min-width: 180px;
        z-index: 100;
        overflow: hidden;
    }

    .dropdown-header {
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: var(--text-muted);
        border-bottom: 1px solid var(--border-color);
    }

    .dropdown-item {
        display: block;
        padding: 0.6rem 1rem;
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.875rem;
    }

    .dropdown-item:hover {
        background: var(--color-surface-700);
    }
</style>
