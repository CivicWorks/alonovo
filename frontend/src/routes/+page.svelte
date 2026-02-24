<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchValues, fetchSectors, voteForCompany, fetchVoteLeaderboard } from '$lib/api';
    import { getGradeClass, computeOverallGrade } from '$lib/utils';
    import type { Company, ValueDef } from '$lib/types';
    import UserMenu from '$lib/UserMenu.svelte';

    let companies: Company[] = $state([]);
    let values: ValueDef[] = $state([]);
    let sectors: string[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    // Voting state
    let votedTickers: Set<string> = $state(new Set());
    let showLeaderboard = $state(false);
    let leaderboard: {ticker: string, name: string, sector: string, vote_count: number}[] = $state([]);

    async function handleVote(ticker: string | null) {
        if (!ticker) return;
        try {
            await voteForCompany(ticker);
            votedTickers = new Set([...votedTickers, ticker]);
        } catch (e) {
            // silently fail
        }
    }

    async function openLeaderboard() {
        leaderboard = await fetchVoteLeaderboard();
        showLeaderboard = true;
    }

    let search = $state('');
    let sectorFilter = $state('');
    let gradeFilter = $state('');
    let valueFilter = $state('');
    let sortDir: 'none' | 'asc' | 'desc' = $state('none');

    onMount(async () => {
        try {
            [companies, values, sectors] = await Promise.all([
                fetchCompanies(),
                fetchValues(),
                fetchSectors(),
            ]);
        } catch (e) {
            error = 'Failed to load companies';
        } finally {
            loading = false;
        }
    });

    function avgScore(c: Company): number {
        const snaps = c.value_snapshots;
        if (!snaps || snaps.length === 0) return 0;
        return snaps.reduce((sum, s) => sum + s.score, 0) / snaps.length;
    }

    function toggleSort() {
        if (sortDir === 'none') sortDir = 'desc';
        else if (sortDir === 'desc') sortDir = 'asc';
        else sortDir = 'none';
    }

    const filtered = $derived.by(() => {
        let result = companies.filter(c => {
            const matchSearch = !search ||
                c.name.toLowerCase().includes(search.toLowerCase()) ||
                (c.ticker && c.ticker.toLowerCase().includes(search.toLowerCase()));
            const matchSector = !sectorFilter || c.sector === sectorFilter;

            let matchGrade = true;
            if (gradeFilter) {
                const overall = computeOverallGrade(c, values);
                matchGrade = !!(overall && overall.startsWith(gradeFilter));
            }

            const matchValue = !valueFilter ||
                c.value_snapshots?.some(s => s.value_slug === valueFilter);

            return matchSearch && matchSector && matchGrade && matchValue;
        });

        if (sortDir !== 'none') {
            const disqualifying = new Set(values.filter(v => v.is_disqualifying).map(v => v.slug));
            result = [...result].sort((a, b) => {
                const sa = avgScore(a);
                const sb = avgScore(b);
                // Disqualified companies sink to bottom (desc) or rise to top (asc)
                const aDisq = a.value_snapshots?.some(s => disqualifying.has(s.value_slug) && s.grade.startsWith('F'));
                const bDisq = b.value_snapshots?.some(s => disqualifying.has(s.value_slug) && s.grade.startsWith('F'));
                if (aDisq && !bDisq) return sortDir === 'desc' ? 1 : -1;
                if (!aDisq && bDisq) return sortDir === 'desc' ? -1 : 1;
                return sortDir === 'desc' ? sb - sa : sa - sb;
            });
        }

        return result;
    });

    const FEATURED_TICKERS = new Set([
        'COST', 'WMT', 'AMZN', 'AAPL', 'TGT', 'GOOGL', 'AAL', 'UAL',
        'T', 'VZ', 'EL', 'BAC', 'KO', 'DELL', 'DIS', 'HPQ', 'XOM', 'GPS', 'V'
    ]);
    const FEATURED_NAMES = new Set(['Avon']);

    function isFeatured(c: Company): boolean {
        return (!!c.ticker && FEATURED_TICKERS.has(c.ticker)) ||
               FEATURED_NAMES.has(c.name);
    }

    const hasActiveFilters = $derived(!!search || !!sectorFilter || !!gradeFilter || !!valueFilter);

    function getCardHighlights(company: Company) {
        if (!company.value_snapshots) return [];
        return company.value_snapshots
            .filter(s => s.highlight_on_card)
            .sort((a, b) => a.highlight_priority - b.highlight_priority);
    }
</script>

<header>
    <div class="header-top">
        <div class="header-stats">
            {#if !loading && !error}
                <span>{filtered.length} Companies</span>
                <span>{values.length} Values</span>
                <span>{sectors.length} Sectors</span>
            {/if}
        </div>
        <UserMenu />
    </div>
    <h1>Alonovo</h1>
    <p class="tagline">Know before you buy. Know before you invest.</p>
    <p class="tagline">
        Joint project of
        <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
        and
        <a href="https://civ.works" target="_blank" rel="noreferrer">Civic Works</a>
    </p>
</header>

<main>
    {#if loading}
        <div class="loading">Loading companies...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else}
        <div class="filters">
            <input type="text" placeholder="Search companies..." bind:value={search} />
            <select bind:value={sectorFilter}>
                <option value="">All Sectors</option>
                {#each sectors as sector}
                    <option value={sector}>{sector}</option>
                {/each}
            </select>
            <select bind:value={valueFilter}>
                <option value="">All Values</option>
                {#each values as v}
                    <option value={v.slug}>{v.name}</option>
                {/each}
            </select>
            <select bind:value={gradeFilter}>
                <option value="">All Grades</option>
                <option value="A">A grades</option>
                <option value="B">B grades</option>
                <option value="C">C grades</option>
                <option value="D">D grades</option>
                <option value="F">F grade</option>
            </select>
            <button class="sort-btn" onclick={toggleSort} title="Sort by grade">
                {#if sortDir === 'none'}
                    Grade ↕
                {:else if sortDir === 'desc'}
                    Best first ↓
                {:else}
                    Worst first ↑
                {/if}
            </button>
        </div>

        {#if !hasActiveFilters}
            {@const featuredList = filtered.filter(c => isFeatured(c))}
            {@const restList = filtered.filter(c => !isFeatured(c))}
            {#if featuredList.length > 0}
                <h2 class="section-heading">Featured Companies</h2>
                <div class="company-grid">
                    {#each featuredList as company}
                        {@const highlights = getCardHighlights(company)}
                        {@const overall = computeOverallGrade(company, values)}
                        <a href="{base}/company/{company.ticker}" class="company-card">
                            <div class="card-header">
                                <div>
                                    <h3 class="company-name">{company.name}</h3>
                                    {#if company.ticker}
                                        <span class="company-ticker">{company.ticker}</span>
                                    {/if}
                                </div>
                                {#if overall}
                                    <div class="grade-badge {getGradeClass(overall)}">{overall}</div>
                                {/if}
                            </div>
                            <div class="card-body">
                                <div class="sector">{company.sector}</div>
                                {#if highlights.length > 0}
                                    <div class="highlights">
                                        {#each highlights as snap}
                                            <div class="highlight {getGradeClass(snap.grade)}">
                                                <span class="highlight-text">{snap.display_text}</span>
                                                <span class="highlight-grade">{snap.grade}</span>
                                            </div>
                                        {/each}
                                    </div>
                                {/if}
                                {#if company.badges && company.badges.length > 0}
                                    <div class="badges">
                                        {#each company.badges as badge}
                                            <span class="badge badge-{badge.type}">{badge.label}</span>
                                        {/each}
                                    </div>
                                {/if}
                                {#if !overall && company.ticker}
                                    <div class="no-data-notice">
                                        {#if votedTickers.has(company.ticker)}
                                            <span class="voted-msg">Thanks! Your vote has been recorded.</span>
                                        {:else}
                                            <span>No data yet</span>
                                            <button class="vote-btn" onclick={(e) => { e.preventDefault(); e.stopPropagation(); handleVote(company.ticker); }}>
                                                Vote to prioritize
                                            </button>
                                        {/if}
                                    </div>
                                {/if}
                                <div class="community-link">
                                    <span class="community-link-text"
                                       role="link"
                                       tabindex="0"
                                       onclick={(e) => { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); }}
                                       onkeydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); } }}>
                                        Community attestations &rarr;
                                    </span>
                                </div>
                            </div>
                        </a>
                    {/each}
                </div>

                <h2 class="section-heading">All Companies</h2>
            {/if}
            <div class="company-grid">
                {#each restList as company}
                    {@const highlights = getCardHighlights(company)}
                    {@const overall = computeOverallGrade(company, values)}
                    <a href="{base}/company/{company.ticker}" class="company-card">
                        <div class="card-header">
                            <div>
                                <h3 class="company-name">{company.name}</h3>
                                {#if company.ticker}
                                    <span class="company-ticker">{company.ticker}</span>
                                {/if}
                            </div>
                            {#if overall}
                                <div class="grade-badge {getGradeClass(overall)}">{overall}</div>
                            {/if}
                        </div>
                        <div class="card-body">
                            <div class="sector">{company.sector}</div>
                            {#if highlights.length > 0}
                                <div class="highlights">
                                    {#each highlights as snap}
                                        <div class="highlight {getGradeClass(snap.grade)}">
                                            <span class="highlight-text">{snap.display_text}</span>
                                            <span class="highlight-grade">{snap.grade}</span>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                            {#if company.badges && company.badges.length > 0}
                                <div class="badges">
                                    {#each company.badges as badge}
                                        <span class="badge badge-{badge.type}">{badge.label}</span>
                                    {/each}
                                </div>
                            {/if}
                            <div class="community-link">
                                <span class="community-link-text"
                                   role="link"
                                   tabindex="0"
                                   onclick={(e) => { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); }}
                                   onkeydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); } }}>
                                    Community attestations &rarr;
                                </span>
                            </div>
                        </div>
                    </a>
                {/each}
            </div>
        {:else}
            <div class="company-grid">
                {#each filtered as company}
                    {@const highlights = getCardHighlights(company)}
                    {@const overall = computeOverallGrade(company, values)}
                    <a href="{base}/company/{company.ticker}" class="company-card">
                        <div class="card-header">
                            <div>
                                <h3 class="company-name">{company.name}</h3>
                                {#if company.ticker}
                                    <span class="company-ticker">{company.ticker}</span>
                                {/if}
                            </div>
                            {#if overall}
                                <div class="grade-badge {getGradeClass(overall)}">{overall}</div>
                            {/if}
                        </div>
                        <div class="card-body">
                            <div class="sector">{company.sector}</div>
                            {#if highlights.length > 0}
                                <div class="highlights">
                                    {#each highlights as snap}
                                        <div class="highlight {getGradeClass(snap.grade)}">
                                            <span class="highlight-text">{snap.display_text}</span>
                                            <span class="highlight-grade">{snap.grade}</span>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                            {#if company.badges && company.badges.length > 0}
                                <div class="badges">
                                    {#each company.badges as badge}
                                        <span class="badge badge-{badge.type}">{badge.label}</span>
                                    {/each}
                                </div>
                            {/if}
                            <div class="community-link">
                                <span class="community-link-text"
                                   role="link"
                                   tabindex="0"
                                   onclick={(e) => { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); }}
                                   onkeydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); window.open(`https://live.linkedtrust.us/?search=${encodeURIComponent(company.name)}`, '_blank'); } }}>
                                    Community attestations &rarr;
                                </span>
                            </div>
                        </div>
                    </a>
                {/each}
            </div>
        {/if}

        <div class="backlog-link">
            <button class="backlog-btn" onclick={openLeaderboard}>
                View data request backlog
            </button>
        </div>
    {/if}
</main>

{#if showLeaderboard}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-overlay" onclick={() => showLeaderboard = false}>
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="modal" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <h2>Data Request Backlog</h2>
                <button class="modal-close" onclick={() => showLeaderboard = false}>&times;</button>
            </div>
            <p class="modal-desc">Companies ranked by community votes. Upvoting helps us prioritize which companies to research next.</p>
            {#if leaderboard.length === 0}
                <p class="modal-empty">No votes yet. Vote on company cards to prioritize data collection!</p>
            {:else}
                <div class="leaderboard">
                    {#each leaderboard as entry, i}
                        <div class="leaderboard-row">
                            <span class="leaderboard-rank">#{i + 1}</span>
                            <div class="leaderboard-info">
                                <span class="leaderboard-name">{entry.name}</span>
                                <span class="leaderboard-sector">{entry.sector}</span>
                            </div>
                            <span class="leaderboard-votes">{entry.vote_count} vote{entry.vote_count === 1 ? '' : 's'}</span>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
{/if}

<footer>
    <p>Data sources: <a href="https://www.opensecrets.org" target="_blank">OpenSecrets</a>,
    <a href="https://www.bbfaw.com" target="_blank">BBFAW</a>,
    <a href="https://www.eggtrack.com" target="_blank">EggTrack</a>,
    <a href="https://www.usaspending.gov" target="_blank">USASpending</a>, and more</p>
    <p><strong>Alonovo</strong> - Guiding capital toward ethical companies</p>
    <p><a href="{base}/about">About</a></p>
</footer>
