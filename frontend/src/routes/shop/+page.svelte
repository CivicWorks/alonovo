<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchBrands, fetchCompanies, fetchProductCategories, fetchProductsByCategory, fetchValues } from '$lib/api';
    import { computeOverallGrade, getGradeClass } from '$lib/utils';
    import type { BrandMapping, Company, Product } from '$lib/types';

    // Plain-word meaning of each letter, from the Alonovo grading table
    const GRADE_WORDS: Record<string, string> = { A: 'Very good', B: 'Good', C: 'Fair', D: 'Poor', F: 'Avoid' };
    const GRADE_RANK: Record<string, number> = { A: 5, B: 4, C: 3, D: 2, F: 1 };

    let products: Product[] = $state([]);
    let brands: BrandMapping[] = $state([]);
    let companies: Company[] = $state([]);
    let categories: {category: string, count: number}[] = $state([]);
    let gradeByTicker: Record<string, string | null> = $state({});
    let loading = $state(true);
    let error = $state('');

    let query = $state('');
    let category = $state('');

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        query = params.get('q') || '';
        category = params.get('category') || '';
        try {
            const [cs, values, b, cats] = await Promise.all([
                fetchCompanies(), fetchValues(), fetchBrands(), fetchProductCategories(),
            ]);
            const grades: Record<string, string | null> = {};
            for (const c of cs) {
                if (c.ticker) grades[c.ticker] = computeOverallGrade(c, values);
            }
            gradeByTicker = grades;
            companies = cs.filter(c => c.ticker);
            brands = b;
            categories = cats;
            products = (await Promise.all(cats.map(c => fetchProductsByCategory(c.category)))).flat();
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load';
        } finally {
            loading = false;
        }
    });

    // Keep the search in the URL so a result can be shared or bookmarked
    $effect(() => {
        const params = new URLSearchParams();
        if (query.trim()) params.set('q', query.trim());
        if (category) params.set('category', category);
        const qs = params.toString();
        history.replaceState(history.state, '', qs ? `?${qs}` : window.location.pathname);
    });

    function gradeOf(ticker: string): string | null {
        return gradeByTicker[ticker] ?? null;
    }

    function rank(grade: string | null): number {
        return grade ? GRADE_RANK[grade.charAt(0)] ?? 0 : 0;
    }

    function categoryLabel(slug: string): string {
        const s = slug.replace(/_/g, ' ');
        return s.charAt(0).toUpperCase() + s.slice(1);
    }

    let needle = $derived(query.trim().toLowerCase());

    let brandResults = $derived(
        needle && !category
            ? brands
                .filter(b => b.brand_name.toLowerCase().includes(needle) || b.company_name.toLowerCase().includes(needle))
                .sort((a, b) => a.brand_name.localeCompare(b.brand_name))
            : []
    );

    let companyResults = $derived(
        needle && !category
            ? companies
                .filter(c => c.name.toLowerCase().includes(needle))
                .sort((a, b) => a.name.localeCompare(b.name))
            : []
    );

    let productResults = $derived(
        products
            .filter(p => !category || p.category === category)
            .filter(p => !needle
                || p.name.toLowerCase().includes(needle)
                || p.brand_name.toLowerCase().includes(needle)
                || p.company_name.toLowerCase().includes(needle))
            .sort((a, b) => rank(gradeOf(b.company_ticker)) - rank(gradeOf(a.company_ticker)) || a.name.localeCompare(b.name))
    );

    let showProducts = $derived(Boolean(needle || category));

    // Better-graded products in the same category, best first, other companies only
    function alternatives(p: Product): Product[] {
        const mine = rank(gradeOf(p.company_ticker));
        const seen = new Set<string>();
        return products
            .filter(o => o.category === p.category && o.company_ticker !== p.company_ticker && rank(gradeOf(o.company_ticker)) > mine)
            .sort((a, b) => rank(gradeOf(b.company_ticker)) - rank(gradeOf(a.company_ticker)))
            .filter(o => !seen.has(o.company_ticker) && seen.add(o.company_ticker))
            .slice(0, 2);
    }
</script>

<svelte:head>
    <title>Shop — Alonovo</title>
</svelte:head>

<div class="shop-page">
    <a href="{base}/" class="back-link">&larr; All companies</a>

    <h1>Who makes it?</h1>
    <p class="subtitle">Search a brand, product or company to see the grade of the company behind it.</p>

    <form class="search" role="search" onsubmit={(e) => e.preventDefault()}>
        <label for="shop-q" class="visually-hidden">Brand or product</label>
        <input id="shop-q" type="search" placeholder="Tide, Cheerios, Nike…" bind:value={query} autocomplete="off" />
    </form>

    {#if categories.length}
        <div class="chips" aria-label="Browse by category">
            {#each categories as c}
                <button type="button" class="chip" class:active={category === c.category}
                    aria-pressed={category === c.category}
                    onclick={() => category = category === c.category ? '' : c.category}>
                    {categoryLabel(c.category)}
                </button>
            {/each}
        </div>
    {/if}

    {#if loading}
        <p class="status">Loading&hellip;</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <p class="status" aria-live="polite">
            {#if showProducts}
                {@const n = companyResults.length + brandResults.length + productResults.length}
                {n} {n === 1 ? 'result' : 'results'}
            {/if}
        </p>

        {#if companyResults.length}
            <section>
                <h2>Companies</h2>
                <ul class="results">
                    {#each companyResults as c}
                        {@const g = gradeOf(c.ticker)}
                        <li>
                            <a class="row" href="{base}/company/{c.ticker}">
                                <span class="main">
                                    <span class="name">{c.name}</span>
                                    {#if c.sector}<span class="owner">{c.sector}</span>{/if}
                                </span>
                                {#if g}
                                    <span class="grade"><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span><span class="grade-badge {getGradeClass(g)}">{g}</span></span>
                                {:else}
                                    <span class="ungraded">Not graded yet</span>
                                {/if}
                            </a>
                        </li>
                    {/each}
                </ul>
            </section>
        {/if}

        {#if brandResults.length}
            <section>
                <h2>Brands</h2>
                <ul class="results">
                    {#each brandResults as b}
                        {@const g = gradeOf(b.company_ticker)}
                        <li>
                            <a class="row" href="{base}/company/{b.company_ticker}">
                                <span class="main">
                                    <span class="name">{b.brand_name}</span>
                                    <span class="owner">by {b.company_name}</span>
                                </span>
                                {#if g}
                                    <span class="grade"><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span><span class="grade-badge {getGradeClass(g)}">{g}</span></span>
                                {:else}
                                    <span class="ungraded">Not graded yet</span>
                                {/if}
                            </a>
                        </li>
                    {/each}
                </ul>
            </section>
        {/if}

        {#if showProducts}
            {#if productResults.length}
                <section>
                    <h2>{category ? categoryLabel(category) : 'Products'}</h2>
                    <ul class="results">
                        {#each productResults as p}
                            {@const g = gradeOf(p.company_ticker)}
                            {@const alts = alternatives(p)}
                            <li>
                                <a class="row" href="{base}/company/{p.company_ticker}">
                                    <span class="main">
                                        <span class="name">{p.name}</span>
                                        <span class="owner">{p.brand_name} &middot; {p.company_name}</span>
                                    </span>
                                    {#if g}
                                        <span class="grade"><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span><span class="grade-badge {getGradeClass(g)}">{g}</span></span>
                                    {:else}
                                        <span class="ungraded">Not graded yet</span>
                                    {/if}
                                </a>
                                {#if alts.length}
                                    <p class="alts">Better:
                                        {#each alts as a, i}
                                            {@const ag = gradeOf(a.company_ticker)}
                                            {#if i > 0}, {/if}<a href="{base}/company/{a.company_ticker}">{a.name}</a> <span class="alt-grade {getGradeClass(ag || '')}">{ag}</span>
                                        {/each}
                                    </p>
                                {/if}
                            </li>
                        {/each}
                    </ul>
                </section>
            {:else if !brandResults.length && !companyResults.length}
                <p class="empty">No match for &ldquo;{query.trim()}&rdquo;. Alonovo covers {companies.length} companies, {brands.length} brands and {products.length} grocery and household products so far.</p>
            {/if}
        {/if}
    {/if}
</div>

<style>
    .shop-page { max-width: 720px; margin: 0 auto; padding: 1rem 0 3rem; }
    .back-link { display: inline-block; margin-bottom: 1rem; text-decoration: none; color: var(--text-muted); }
    .back-link:hover { color: var(--accent); }
    h1 { margin: 0 0 0.25rem; }
    .subtitle { color: var(--text-secondary); margin: 0 0 1.25rem; }

    .search input {
        width: 100%;
        box-sizing: border-box;
        font-size: 1.15rem;
        padding: 0.85rem 1rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        background: var(--bg-input);
        color: var(--text-primary);
    }
    .search input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
    .visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

    .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.9rem 0 0; }
    .chip {
        font: inherit;
        font-size: 0.85rem;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
        color: var(--text-secondary);
        cursor: pointer;
    }
    .chip:hover { border-color: var(--accent); }
    .chip.active { background: var(--accent); border-color: var(--accent); color: var(--bg-primary); }

    .status { color: var(--text-muted); font-size: 0.85rem; min-height: 1.2em; margin: 1rem 0 0.25rem; }
    h2 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 1.25rem 0 0.4rem; }

    .results { list-style: none; margin: 0; padding: 0; }
    .results li { border-top: 1px solid var(--border-color); }
    .row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.7rem 0.25rem;
        text-decoration: none;
        color: inherit;
    }
    .row:hover .name { color: var(--accent); }
    .main { display: flex; flex-direction: column; min-width: 0; }
    .name { font-weight: 600; }
    .owner { color: var(--text-muted); font-size: 0.85rem; }
    .grade { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
    .grade-word { color: var(--text-secondary); font-size: 0.85rem; }
    .grade .grade-badge { font-size: 1.1rem; min-width: 44px; }
    .ungraded { color: var(--text-muted); font-size: 0.85rem; flex-shrink: 0; }

    .alts { margin: -0.3rem 0 0.7rem 0.25rem; font-size: 0.85rem; color: var(--text-muted); }
    .alts a { color: var(--text-secondary); }
    .alt-grade { font-size: 0.75rem; font-weight: 700; padding: 0 0.3rem; border-radius: 0.2rem; }

    .empty { color: var(--text-secondary); margin-top: 1rem; }
    .error { color: #ef4444; }
</style>
