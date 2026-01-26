<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchCompanies } from '$lib/api';
    import { formatMoney, getGradeClass } from '$lib/utils';
    import type { Company } from '$lib/types';

    let companies: Company[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    let search = $state('');
    let sectorFilter = $state('');
    let gradeFilter = $state('');

    onMount(async () => {
        try {
            companies = await fetchCompanies();
        } catch (e) {
            error = 'Failed to load companies';
        } finally {
            loading = false;
        }
    });

    const sectors = $derived([...new Set(companies.map(c => c.sector))].sort());

    const filtered = $derived(companies.filter(c => {
        const matchSearch = !search ||
            c.name.toLowerCase().includes(search.toLowerCase()) ||
            c.ticker.toLowerCase().includes(search.toLowerCase());
        const matchSector = !sectorFilter || c.sector === sectorFilter;
        const score = c.scores[0];
        const matchGrade = !gradeFilter || (score && score.grade.startsWith(gradeFilter));
        return matchSearch && matchSector && matchGrade;
    }));

    const stats = $derived(() => {
        const grades = filtered.map(c => c.scores[0]?.grade.charAt(0) || '');
        const aCount = grades.filter(g => g === 'A').length;
        const fCount = grades.filter(g => g === 'F').length;
        const totalSpend = filtered.reduce((sum, c) => sum + (c.scores[0]?.raw_value || 0), 0);
        return { total: filtered.length, aCount, fCount, totalSpend };
    });
</script>

<header>
    <h1>Alonovo</h1>
    <p class="tagline">Know before you buy. Know before you invest.</p>
    <p class="tagline">
        Grades powered by
        <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
    </p>
</header>

<main>
    <section class="intro">
        <h2>Corporate Lobbying Grades</h2>
        <p>How much do these companies spend to influence government policy?<br>
        <em>Lower spending = Better grade</em></p>
    </section>

    {#if loading}
        <div class="loading">Loading companies...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else}
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">{stats().total}</div>
                <div class="stat-label">Companies</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats().aCount}</div>
                <div class="stat-label">A Grades</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats().fCount}</div>
                <div class="stat-label">F Grades</div>
            </div>
            <div class="stat">
                <div class="stat-value">{formatMoney(stats().totalSpend)}</div>
                <div class="stat-label">Total Lobbying</div>
            </div>
        </div>

        <div class="filters">
            <input type="text" placeholder="Search companies..." bind:value={search} />
            <select bind:value={sectorFilter}>
                <option value="">All Sectors</option>
                {#each sectors as sector}
                    <option value={sector}>{sector}</option>
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
        </div>

        <div class="company-grid">
            {#each filtered as company}
                {@const score = company.scores[0]}
                <a href="/company/{company.ticker}" class="company-card">
                    <div class="card-header">
                        <div>
                            <h3 class="company-name">{company.name}</h3>
                            <span class="company-ticker">{company.ticker}</span>
                        </div>
                        {#if score}
                            <div class="grade-badge {getGradeClass(score.grade)}">{score.grade}</div>
                        {/if}
                    </div>
                    <div class="card-body">
                        <div class="sector">{company.sector}</div>
                        {#if score}
                            <div class="spend">Lobbying: <strong>{formatMoney(score.raw_value)}</strong> (2024)</div>
                            <div class="grade-reason">{score.reason}</div>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</main>

<footer>
    <p>Data sources: <a href="https://www.opensecrets.org" target="_blank">OpenSecrets</a>,
    <a href="https://www.statista.com" target="_blank">Statista</a> (2024)</p>
    <p><strong>Alonovo</strong> - Guiding capital toward ethical companies</p>
</footer>
