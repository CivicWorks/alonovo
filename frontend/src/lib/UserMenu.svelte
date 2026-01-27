<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchCurrentUser, getLoginUrl, getLogoutUrl } from '$lib/api';
    import type { User } from '$lib/types';

    let user: User | null = $state(null);
    let menuOpen = $state(false);

    onMount(async () => {
        user = await fetchCurrentUser();
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
                <a href="/profile" class="dropdown-item">Profile</a>
                {#if user.is_staff}
                    <a href="/admin/" class="dropdown-item">Admin</a>
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
        color: white;
        opacity: 0.9;
        text-decoration: none;
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 6px;
        transition: opacity 0.2s;
    }

    .sign-in:hover {
        opacity: 1;
        background: rgba(255,255,255,0.1);
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255,255,255,0.25);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background 0.2s;
    }

    .avatar:hover {
        background: rgba(255,255,255,0.4);
    }

    .dropdown {
        position: absolute;
        top: 44px;
        right: 0;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        min-width: 180px;
        z-index: 100;
        overflow: hidden;
    }

    .dropdown-header {
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: #666;
        border-bottom: 1px solid #eee;
    }

    .dropdown-item {
        display: block;
        padding: 0.6rem 1rem;
        color: #333;
        text-decoration: none;
        font-size: 0.9rem;
    }

    .dropdown-item:hover {
        background: #f5f5f5;
    }
</style>
