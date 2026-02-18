<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { fetchCompany, fetchCompanyClaims, fetchValues } from '$lib/api';
    import { getGradeClass, computeOverallGrade, groupValues } from '$lib/utils';
    import type { Company, ClaimData, ValueDef, ValueGroup } from '$lib/types';
    import { loadUser, loadWeights, getWeights, isPersonalized } from '$lib/stores.svelte';
    import UserMenu from '$lib/UserMenu.svelte';
    import PersonalizationToggle from '$lib/PersonalizationToggle.svelte';

    let company: Company | null = $state(null);
    let claims: ClaimData[] = $state([]);
    let values: ValueDef[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    onMount(async () => {
        try {
            const ticker = $page.params.ticker;
            [company, claims, values] = await Promise.all([
                fetchCompany(ticker),
                fetchCompanyClaims(ticker),
                fetchValues(),
            ]);
            const user = await loadUser();
            if (user) await loadWeights();
        } catch (e) {
            error = 'Failed to load company';
        } finally {
            loading = false;
        }
    });

    const activeWeights = $derived(isPersonalized() ? getWeights() : undefined);

    function claimsForSnapshot(claimUris: string[]): ClaimData[] {
        return claims.filter(c => claimUris.includes(c.uri));
    }

    function formatSource(uri: string): string {
        try {
            const url = new URL(uri);
            return url.hostname.replace('www.', '');
        } catch {
            return uri;
        }
    }

    function formatClaimType(type: string): string {
        return type.replace(/_/g, ' ').toLowerCase()
            .replace(/\b\w/g, c => c.toUpperCase());
    }

    function formatAmount(claim: ClaimData): string {
        if (!claim.amt) return '';
        const amt = parseFloat(claim.amt);
        if (claim.unit === 'USD') {
            if (amt >= 1000000) return `$${(amt / 1000000).toFixed(1)}M`;
            if (amt >= 1000) return `$${(amt / 1000).toFixed(0)}K`;
            return `$${amt.toFixed(0)}`;
        }
        if (claim.unit === 'million_usd') return `$${amt}M`;
        if (claim.unit === 'percent') return `${amt}%`;
        return `${amt} ${claim.unit || ''}`.trim();
    }
</script>

<header class="detail-banner">
    <a href="{base}/" class="back-link">&larr; Alonovo</a>
    <div class="banner-right">
        <PersonalizationToggle />
        <UserMenu />
    </div>
</header>

<div class="container">

    {#if loading}
        <div class="loading">Loading...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else if company}
        <div class="company-detail">
            <div class="detail-header">
                <div>
                    <h2>{company.name}</h2>
                    <div class="detail-meta">
                        {#if company.ticker}
                            <span class="ticker">{company.ticker}</span>
                        {/if}
                        {#if company.sector}
                            <span class="sector-tag">{company.sector}</span>
                        {/if}
                    </div>
                </div>
                {#if true}
                    {@const overall = computeOverallGrade(company, values, activeWeights)}
                    {#if overall}
                        <div class="grade-badge {getGradeClass(overall)}">
                            {overall}
                        </div>
                    {/if}
                {/if}
            </div>

            {#if company.badges && company.badges.length > 0}
                <div class="badges">
                    {#each company.badges as badge}
                        <span class="badge badge-{badge.type}">{badge.label}</span>
                    {/each}
                </div>
            {/if}

            {#if company.value_snapshots && company.value_snapshots.length > 0}
                {#if true}
                    {@const groups = groupValues(values, company.value_snapshots, activeWeights)}
                    <section class="claims-section">
                        <h3>Value Ratings</h3>
                        {#each groups as group}
                            <div class="value-group">
                                {#if group.values.length > 1}
                                    <div class="group-header">
                                        <div class="group-name">{group.groupName}</div>
                                        <div class="claim-grade {getGradeClass(group.grade)}">{group.grade}</div>
                                    </div>
                                {/if}
                                <div class="claim-cards" class:grouped={group.values.length > 1}>
                                    {#each group.snapshots as snap}
                                        {@const snapClaims = claimsForSnapshot(snap.claim_uris || [])}
                                        <div class="claim-card">
                                            <div class="claim-card-header">
                                                <div class="claim-value-name">{snap.value_name}</div>
                                                <div class="claim-grade {getGradeClass(snap.grade)}">{snap.grade}</div>
                                            </div>
                                            <div class="claim-display">{snap.display_text}</div>
                                            {#if snapClaims.length > 0}
                                                <div class="claim-sources">
                                                    {#each snapClaims as claim}
                                                        <div class="source-row">
                                                            <div class="source-detail">
                                                                <span class="source-type">{formatClaimType(claim.claim_type)}</span>
                                                                {#if claim.amt}
                                                                    <span class="source-amount">{formatAmount(claim)}</span>
                                                                {/if}
                                                                {#if claim.label}
                                                                    <span class="source-label">{claim.label}</span>
                                                                {/if}
                                                                {#if claim.effective_date}
                                                                    <span class="source-date">{claim.effective_date}</span>
                                                                {/if}
                                                            </div>
                                                            {#if claim.source_uri}
                                                                <a href={claim.source_uri} target="_blank" rel="noreferrer" class="source-link">
                                                                    {formatSource(claim.source_uri)}
                                                                </a>
                                                            {/if}
                                                            {#if claim.how_known}
                                                                <span class="how-known">{claim.how_known.replace(/_/g, ' ')}</span>
                                                            {/if}
                                                        </div>
                                                    {/each}
                                                </div>
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        {/each}
                    </section>
                {/if}
            {/if}

        </div>
    {/if}
</div>

<style>
    .detail-banner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(135deg, #1a5f2a 0%, #2d8a3e 100%);
        color: white;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
    }

    .back-link {
        color: rgba(255,255,255,0.85);
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .back-link:hover {
        color: white;
    }

    .banner-right {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }

    .detail-meta {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.25rem;
    }

    .ticker {
        color: #888;
        font-size: 0.9rem;
    }

    .sector-tag {
        background: #f3f4f6;
        color: #4b5563;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }

    .claims-section h3 {
        margin-bottom: 1rem;
    }

    .value-group {
        margin-bottom: 1.5rem;
    }

    .group-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 1rem;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }

    .group-name {
        font-weight: 700;
        font-size: 1rem;
        color: #15803d;
    }

    .claim-cards {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .claim-cards.grouped {
        margin-left: 1rem;
        border-left: 2px solid #bbf7d0;
        padding-left: 1rem;
    }

    .claim-card {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        background: #fafafa;
    }

    .claim-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .claim-value-name {
        font-weight: 600;
        color: #1a5f2a;
    }

    .claim-grade {
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        min-width: 42px;
        text-align: center;
    }

    .claim-grade.grade-A { background: #22c55e; color: white; }
    .claim-grade.grade-B { background: #84cc16; color: white; }
    .claim-grade.grade-C { background: #eab308; color: #1a1a1a; }
    .claim-grade.grade-D { background: #f97316; color: white; }
    .claim-grade.grade-F { background: #ef4444; color: white; }

    .claim-display {
        font-size: 0.95rem;
        color: #444;
        margin-bottom: 0.75rem;
    }

    .claim-sources {
        border-top: 1px solid #e5e7eb;
        padding-top: 0.5rem;
    }

    .source-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0;
        font-size: 0.8rem;
    }

    .source-row + .source-row {
        border-top: 1px solid #f0f0f0;
    }

    .source-detail {
        display: flex;
        gap: 0.4rem;
        align-items: center;
        flex: 1;
    }

    .source-type {
        font-weight: 500;
        color: #555;
    }

    .source-amount {
        font-weight: 600;
        color: #1a1a1a;
    }

    .source-label {
        color: #666;
        font-style: italic;
    }

    .source-date {
        color: #999;
    }

    .source-link {
        color: #1a5f2a;
        text-decoration: none;
        font-size: 0.75rem;
        padding: 0.15rem 0.4rem;
        background: #dcfce7;
        border-radius: 3px;
    }

    .source-link:hover {
        background: #bbf7d0;
    }

    .how-known {
        color: #999;
        font-size: 0.7rem;
        text-transform: capitalize;
    }
</style>
