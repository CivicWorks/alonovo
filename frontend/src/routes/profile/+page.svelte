<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCurrentUser, fetchValues } from '$lib/api';
    import type { User, ValueDef } from '$lib/types';
    import { PUBLIC_API_URL } from '$env/static/public';

    let user: User | null = $state(null);
    let values: ValueDef[] = $state([]);
    let weights: Record<string, number> = $state({});
    let loading = $state(true);
    let saving = $state(false);
    let saved = $state(false);

    onMount(async () => {
        try {
            user = await fetchCurrentUser();
            if (!user) {
                window.location.href = '/';
                return;
            }
            values = await fetchValues();

            // Fetch existing weights
            const res = await fetch(`${PUBLIC_API_URL}/me/weights/`, {
                credentials: 'include',
            });
            if (res.ok) {
                const data = await res.json();
                for (const w of data) {
                    weights[w.value_slug] = w.weight;
                }
            }

            // Set defaults for values not yet weighted
            for (const v of values) {
                if (weights[v.slug] === undefined) {
                    weights[v.slug] = 5;
                }
            }
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });

    function getCsrfToken(): string {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    async function saveWeights() {
        saving = true;
        saved = false;
        try {
            const payload = Object.entries(weights).map(([slug, weight]) => ({
                value_slug: slug,
                weight,
            }));
            const res = await fetch(`${PUBLIC_API_URL}/me/weights/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                saved = true;
                setTimeout(() => saved = false, 2000);
            }
        } catch (e) {
            console.error(e);
        } finally {
            saving = false;
        }
    }

    function getWeightLabel(w: number): string {
        if (w === 0) return "Don't care";
        if (w <= 2) return 'Low';
        if (w <= 4) return 'Moderate';
        if (w <= 6) return 'Important';
        if (w <= 8) return 'Very important';
        return 'Critical';
    }
</script>

<div class="container">
    <a href="{base}/" class="back-btn">&larr; Back</a>

    {#if loading}
        <div class="loading">Loading...</div>
    {:else if !user}
        <div class="error">Please sign in to access your profile.</div>
    {:else}
        <div class="profile-page">
            <div class="profile-header">
                <h2>Your Profile</h2>
                <p class="profile-email">{user.email}</p>
            </div>

            <section class="weights-section">
                <h3>Value Weights</h3>
                <p class="weights-intro">
                    Adjust how much each value matters to you when calculating company grades.
                    Higher weight = more influence on the overall score.
                </p>

                <div class="weight-sliders">
                    {#each values.filter(v => !v.is_fixed) as v}
                        <div class="weight-row">
                            <div class="weight-info">
                                <span class="weight-name">{v.name}</span>
                                <span class="weight-desc">{v.description}</span>
                            </div>
                            <div class="weight-control">
                                <input
                                    type="range"
                                    min="0"
                                    max="10"
                                    bind:value={weights[v.slug]}
                                    class="slider"
                                />
                                <div class="weight-value">
                                    <span class="weight-number">{weights[v.slug]}</span>
                                    <span class="weight-label">{getWeightLabel(weights[v.slug])}</span>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>

                {#if values.some(v => v.is_fixed)}
                    <div class="fixed-values">
                        <h4>Always Counted</h4>
                        <p class="weights-intro">These values are always included in scoring and cannot be adjusted.</p>
                        {#each values.filter(v => v.is_fixed) as v}
                            <div class="fixed-row">
                                <span class="weight-name">{v.name}</span>
                                <span class="weight-desc">{v.description}</span>
                            </div>
                        {/each}
                    </div>
                {/if}

                <div class="save-row">
                    <button class="save-btn" onclick={saveWeights} disabled={saving}>
                        {saving ? 'Saving...' : 'Save Weights'}
                    </button>
                    {#if saved}
                        <span class="save-confirm">Saved!</span>
                    {/if}
                </div>
            </section>
        </div>
    {/if}
</div>

<style>
    .profile-page {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .profile-header {
        margin-bottom: 2rem;
    }

    .profile-header h2 {
        color: #1a5f2a;
        margin: 0 0 0.25rem;
    }

    .profile-email {
        color: #888;
        font-size: 0.9rem;
    }

    .weights-section h3 {
        color: #1a5f2a;
        margin: 0 0 0.5rem;
    }

    .weights-intro {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    .weight-sliders {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
    }

    .weight-row {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        background: #fafafa;
    }

    .weight-info {
        margin-bottom: 0.5rem;
    }

    .weight-name {
        font-weight: 600;
        color: #1a1a1a;
    }

    .fixed-values {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e5e7eb;
    }

    .fixed-values h4 {
        color: #1a5f2a;
        margin: 0 0 0.25rem;
    }

    .fixed-row {
        padding: 0.75rem 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        background: #fafafa;
        margin-bottom: 0.5rem;
    }

    .weight-desc {
        display: block;
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.15rem;
    }

    .weight-control {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .slider {
        flex: 1;
        height: 6px;
        -webkit-appearance: none;
        appearance: none;
        background: #e5e7eb;
        border-radius: 3px;
        outline: none;
    }

    .slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #1a5f2a;
        cursor: pointer;
    }

    .slider::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #1a5f2a;
        cursor: pointer;
        border: none;
    }

    .weight-value {
        min-width: 80px;
        text-align: right;
    }

    .weight-number {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1a5f2a;
    }

    .weight-label {
        display: block;
        font-size: 0.7rem;
        color: #888;
    }

    .save-row {
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .save-btn {
        background: linear-gradient(135deg, #1a5f2a 0%, #2d8a3e 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .save-btn:hover { opacity: 0.9; }
    .save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

    .save-confirm {
        color: #22c55e;
        font-weight: 600;
    }
</style>
