<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchValues, fetchSectors } from '$lib/api';
    import { getGradeClass, computeOverallGrade } from '$lib/utils';
    import type { Company, ValueDef } from '$lib/types';
    import UserMenu from '$lib/UserMenu.svelte';

    let companies: Company[] = $state([]);
    let values: ValueDef[] = $state([]);
    let sectors: string[] = $state([]);
    let loading = $state(true);
    let error = $state('');

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
        Grades powered by
        <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
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
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</main>

<footer>
    <p>Data sources: <a href="https://www.opensecrets.org" target="_blank">OpenSecrets</a>,
    <a href="https://www.bbfaw.com" target="_blank">BBFAW</a>,
    <a href="https://www.eggtrack.com" target="_blank">EggTrack</a>,
    <a href="https://www.usaspending.gov" target="_blank">USASpending</a>, and more</p>
    <p><strong>Alonovo</strong> - Guiding capital toward ethical companies</p>
</footer>
