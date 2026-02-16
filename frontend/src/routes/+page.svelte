<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchValues, fetchSectors } from '$lib/api';
    import { getGradeClass, computeOverallGrade, groupValues } from '$lib/utils';
    import type { Company, ValueDef, ValueGroup } from '$lib/types';
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

    /** Build filter options: groups + ungrouped values */
    const filterOptions = $derived.by(() => {
        const seen = new Set<string>();
        const opts: { key: string; label: string; order: number }[] = [];
        for (const v of values) {
            const key = v.display_group || v.slug;
            const label = v.display_group || v.name;
            if (!seen.has(key)) {
                seen.add(key);
                opts.push({ key, label, order: v.display_group_order });
            }
        }
        return opts.sort((a, b) => a.order - b.order);
    });

    function getCompanyGroups(c: Company): ValueGroup[] {
        return groupValues(values, c.value_snapshots || []);
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

            // Filter by group or ungrouped value slug
            let matchValue = true;
            if (valueFilter) {
                const groups = getCompanyGroups(c);
                matchValue = groups.some(g =>
                    g.groupName === valueFilter ||
                    g.values.some(v => v.slug === valueFilter)
                );
            }

            return matchSearch && matchSector && matchGrade && matchValue;
        });

        if (sortDir !== 'none') {
            result = [...result].sort((a, b) => {
                const gradeA = computeOverallGrade(a, values);
                const gradeB = computeOverallGrade(b, values);
                // F grades sink to bottom (desc) or rise to top (asc)
                if (gradeA === 'F' && gradeB !== 'F') return sortDir === 'desc' ? 1 : -1;
                if (gradeA !== 'F' && gradeB === 'F') return sortDir === 'desc' ? -1 : 1;
                const groupsA = getCompanyGroups(a);
                const groupsB = getCompanyGroups(b);
                const sa = groupsA.length ? groupsA.reduce((s, g) => s + g.score, 0) / groupsA.length : 0;
                const sb = groupsB.length ? groupsB.reduce((s, g) => s + g.score, 0) / groupsB.length : 0;
                return sortDir === 'desc' ? sb - sa : sa - sb;
            });
        }

        return result;
    });

</script>

<header>
    <div class="header-top">
        <div class="header-stats">
            {#if !loading && !error}
                <span>{filtered.length} Companies</span>
                <span>{filterOptions.length} Values</span>
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
                {#each filterOptions as opt}
                    <option value={opt.key}>{opt.label}</option>
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
                {#if true}
                    {@const groups = getCompanyGroups(company)}
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
                            {#if groups.length > 0}
                                <div class="highlights">
                                    {#each groups as group}
                                        <div class="highlight {getGradeClass(group.grade)}">
                                            <span class="highlight-text">{group.groupName}</span>
                                            <span class="highlight-grade">{group.grade}</span>
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
                {/if}
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
