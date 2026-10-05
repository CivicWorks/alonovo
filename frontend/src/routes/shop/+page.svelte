<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchBrands, fetchCompanies, fetchProductCategories, fetchProductsByCategory, fetchValues } from '$lib/api';
    import { computeOverallGrade, getGradeClass } from '$lib/utils';
    import type { BrandMapping, Company, Product } from '$lib/types';

    // Plain-word meaning of each letter, from the Alonovo grading table
    const GRADE_WORDS: Record<string, string> = { A: 'Very good', B: 'Good', C: 'Fair', D: 'Poor', F: 'Avoid' };
    const GRADE_RANK: Record<string, number> = { A: 5, B: 4, C: 3, D: 2, F: 1 };
    const FINE_GRADES = ['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'];

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
        document.body.classList.add('shop-light');
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
            const groupKey = new Map(values.map(v => [v.slug, v.display_group || v.slug]));
            groupCount = new Set(groupKey.values()).size;
            const gb: Record<string, number> = {};
            for (const c of cs) {
                if (c.ticker) gb[c.ticker] = new Set((c.value_snapshots || []).map(sn => groupKey.get(sn.value_slug)).filter(Boolean)).size;
            }
            groupsByTicker = gb;
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

    $effect(() => () => document.body.classList.remove('shop-light'));

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
    let words = $derived(needle.split(/\s+/).filter(Boolean));

    function tokens(text: string): string[] {
        return text.toLowerCase().replace(/_/g, ' ').split(/[^a-z0-9'&]+/).filter(Boolean);
    }

    // How well one typed word matches a list of words: whole word (or plural) 3, word start 1
    function wordScore(w: string, toks: string[]): number {
        const stem = w.replace(/e?s$/, '');
        let best = 0;
        for (const t of toks) {
            if (t === w || t === stem || t.replace(/e?s$/, '') === stem) return 3;
            if (t.startsWith(w)) best = 1;
        }
        return best;
    }

    // Every typed word must match; the name counts most, then brand, then company and category
    function score(name: string, brand: string, rest: string): number {
        const n = tokens(name), b = tokens(brand), r = tokens(rest);
        let total = 0;
        for (const w of words) {
            const s = Math.max(wordScore(w, n) * 3, wordScore(w, b) * 2, wordScore(w, r));
            if (!s) return 0;
            total += s;
        }
        if (name.toLowerCase() === needle || brand.toLowerCase() === needle) total += 20;
        // Among equal matches, a name with fewer extra words is the closer match
        return total + words.length / Math.max(n.length, 1);
    }

    function byScoreThenGrade<T>(items: T[], scoreOf: (x: T) => number, tickerOf: (x: T) => string, nameOf: (x: T) => string): T[] {
        return items
            .map(x => ({ x, s: scoreOf(x) }))
            .filter(r => r.s > 0)
            .sort((a, b) => b.s - a.s || rank(gradeOf(tickerOf(b.x))) - rank(gradeOf(tickerOf(a.x))) || nameOf(a.x).localeCompare(nameOf(b.x)))
            .map(r => r.x);
    }

    let brandResults = $derived(
        needle && !category
            ? byScoreThenGrade(brands, b => score(b.brand_name, b.brand_name, b.company_name), b => b.company_ticker, b => b.brand_name)
            : []
    );

    let companyResults = $derived(
        needle && !category
            ? byScoreThenGrade(companies, c => score(c.name, '', ''), c => c.ticker, c => c.name)
            : []
    );

    let productResults = $derived(
        needle
            ? byScoreThenGrade(products.filter(p => !category || p.category === category),
                p => score(p.name, p.brand_name, `${p.company_name} ${p.category}`), p => p.company_ticker, p => p.name)
            : products
                .filter(p => p.category === category)
                .sort((a, b) => rank(gradeOf(b.company_ticker)) - rank(gradeOf(a.company_ticker)) || a.name.localeCompare(b.name))
    );

    let showProducts = $derived(Boolean(needle || category));

    // Position of a grade including its plus or minus; 0 when not graded
    function fineRank(grade: string | null): number {
        return grade ? FINE_GRADES.indexOf(grade) + 1 : 0;
    }

    // Same-type products from other companies with a better grade, for anything graded below A.
    // For products not graded yet, only options graded B- or better.
    function betterOptions(types: string[], ticker: string): Product[] {
        const grade = gradeOf(ticker);
        if (rank(grade) >= GRADE_RANK.A || !types.length) return [];
        const floor = grade ? fineRank(grade) + 1 : fineRank('B-');
        const seen = new Set<string>();
        return products
            .filter(o => o.product_type && types.includes(o.product_type) && o.company_ticker !== ticker && fineRank(gradeOf(o.company_ticker)) >= floor)
            .sort((a, b) => fineRank(gradeOf(b.company_ticker)) - fineRank(gradeOf(a.company_ticker))
                || (groupsByTicker[b.company_ticker] || 0) - (groupsByTicker[a.company_ticker] || 0))
            .filter(o => !seen.has(o.company_ticker) && seen.add(o.company_ticker))
            .slice(0, 2);
    }

    function brandImage(b: BrandMapping): string | null {
        return products.find(p => p.brand_name === b.brand_name && p.image_url)?.image_url ?? null;
    }

    function brandTypes(b: BrandMapping): string[] {
        return [...new Set(products.filter(p => p.brand_name === b.brand_name && p.product_type).map(p => p.product_type as string))];
    }
    let total = $derived(companyResults.length + brandResults.length + productResults.length);

    // Landing page: one row per shopping category, one example product per company.
    // A-graded companies first, then one graded B or C, then one graded D or F, so each aisle
    // shows the spread. Within each, companies graded on at least 2 issues come first, and every
    // card shows how many issues its grade rests on.
    // The row compares one kind of product (water with water) when a kind has two or more
    // graded companies; the kind covering the most grade bands, then the most companies, wins.
    const MIN_ISSUES_PREFERRED = 2;
    const MAX_A_PER_CATEGORY = 4;

    function bandOf(p: Product): string {
        const l = (gradeOf(p.company_ticker) as string).charAt(0);
        return l === 'A' ? 'A' : 'BC'.includes(l) ? 'BC' : 'DF';
    }

    function spreadPicks(items: Product[]): Product[] {
        const seen = new Set<string>();
        const ranked = items
            .filter(p => gradeOf(p.company_ticker))
            .sort((a, b) => Number((groupsByTicker[b.company_ticker] || 0) >= MIN_ISSUES_PREFERRED) - Number((groupsByTicker[a.company_ticker] || 0) >= MIN_ISSUES_PREFERRED)
                || fineRank(gradeOf(b.company_ticker)) - fineRank(gradeOf(a.company_ticker))
                || (groupsByTicker[b.company_ticker] || 0) - (groupsByTicker[a.company_ticker] || 0)
                || Number(Boolean(b.image_url)) - Number(Boolean(a.image_url)))
            .filter(p => !seen.has(p.company_ticker) && seen.add(p.company_ticker));
        return [
            ...ranked.filter(p => bandOf(p) === 'A').slice(0, MAX_A_PER_CATEGORY),
            ...ranked.filter(p => bandOf(p) === 'BC').slice(0, 1),
            ...ranked.filter(p => bandOf(p) === 'DF').slice(0, 1),
        ];
    }

    let topByCategory = $derived(categories.map(c => {
        const inAisle = products.filter(p => p.category === c.category);
        const types = [...new Set(inAisle.map(p => p.product_type).filter(Boolean))] as string[];
        const best = types
            .map(t => ({ type: t, picks: spreadPicks(inAisle.filter(p => p.product_type === t)) }))
            .filter(x => x.picks.length >= 2)
            .sort((x, y) => new Set(y.picks.map(bandOf)).size - new Set(x.picks.map(bandOf)).size
                || y.picks.length - x.picks.length
                || x.type.localeCompare(y.type))[0];
        return best
            ? { category: c.category, type: best.type, picks: best.picks }
            : { category: c.category, type: '', picks: spreadPicks(inAisle) };
    }).filter(c => c.picks.length));

    // Spelling suggestion when nothing matches: closest known word within one or two edits
    let vocabulary = $derived(new Set(
        [...products.flatMap(p => tokens(`${p.name} ${p.brand_name}`)), ...brands.flatMap(b => tokens(b.brand_name)), ...companies.flatMap(c => tokens(c.name))]
            .filter(t => t.length > 2)
    ));

    function distance(a: string, b: string): number {
        const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
        for (let j = 1; j <= b.length; j++) d[0][j] = j;
        for (let i = 1; i <= a.length; i++)
            for (let j = 1; j <= b.length; j++)
                d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        return d[a.length][b.length];
    }

    let suggestion = $derived.by(() => {
        if (!needle || total > 0) return '';
        const fixed = words.map(w => {
            if (vocabulary.has(w)) return w;
            const limit = w.length >= 7 ? 2 : 1;
            let best = '', bestD = limit + 1;
            for (const v of vocabulary) {
                if (Math.abs(v.length - w.length) > limit) continue;
                const dd = distance(w, v);
                if (dd < bestD) { best = v; bestD = dd; }
            }
            return best || w;
        }).join(' ');
        return fixed !== needle ? fixed : '';
    });

    // How many of the issues Alonovo tracks this company's grade rests on
    let groupCount = $state(0);
    let groupsByTicker: Record<string, number> = $state({});

    function coverage(ticker: string): string {
        const n = groupsByTicker[ticker];
        return n ? `graded on ${n} of ${groupCount} issues` : '';
    }
</script>

<svelte:head>
    <title>Shopping for a Better World — Alonovo</title>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
</svelte:head>

{#snippet gradeBlock(g: string | null)}
    {#if g}
        <span class="grade"><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span><span class="grade-badge {getGradeClass(g)}">{g}</span></span>
    {:else}
        <span class="ungraded">Not graded yet</span>
    {/if}
{/snippet}

<!-- One side of a side-by-side pair: what the shopper searched for, or the better option -->
{#snippet card(ticker: string, image: string | null | undefined, name: string, sub: string, tag: string)}
    {@const g = gradeOf(ticker)}
    <a class="card" class:card-better={tag} href="{base}/company/{ticker}">
        {#if tag}<span class="tag">{tag}</span>{/if}
        <span class="card-top">
            <span class="thumb">{#if image}<img src={image} alt="" loading="lazy" />{/if}</span>
            {@render gradeBlock(g)}
        </span>
        <span class="name">{name}</span>
        <span class="owner">{sub}{g && coverage(ticker) ? ` · ${coverage(ticker)}` : ''}</span>
    </a>
{/snippet}

<!-- Row with the best better option beside it, or a plain row when there is none -->
{#snippet result(ticker: string, image: string | null | undefined, name: string, sub: string, options: Product[], showThumb: boolean)}
    {@const g = gradeOf(ticker)}
    {#if options.length}
        {@const o = options[0]}
        <div class="pair">
            {@render card(ticker, image, name, sub, '')}
            {@render card(o.company_ticker, o.image_url, o.name, o.company_name, g ? 'Better' : 'Try')}
        </div>
    {:else}
        <a class="row" href="{base}/company/{ticker}">
            {#if showThumb}<span class="thumb">{#if image}<img src={image} alt="" loading="lazy" />{/if}</span>{/if}
            <span class="main">
                <span class="name">{name}</span>
                <span class="owner">{sub}{g && coverage(ticker) ? ` · ${coverage(ticker)}` : ''}</span>
            </span>
            {@render gradeBlock(g)}
        </a>
    {/if}
{/snippet}

<div class="shop-page">
    <header class="masthead">
        <h1>Shopping for a Better World</h1>
        <a href="{base}/" class="home-link">Alonovo</a>
    </header>

    <form class="search" role="search" onsubmit={(e) => e.preventDefault()}>
        <label for="shop-q" class="visually-hidden">Brand or product</label>
        <input id="shop-q" type="search" placeholder="Cheerios, Tide, peanut butter…" bind:value={query} autocomplete="off" />
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
                {total} {total === 1 ? 'result' : 'results'}
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
                                    <span class="owner">{c.sector}{coverage(c.ticker) ? `${c.sector ? ' · ' : ''}${coverage(c.ticker)}` : ''}</span>
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
                        <li>
                            {@render result(b.company_ticker, brandImage(b), b.brand_name, `by ${b.company_name}`, betterOptions(brandTypes(b), b.company_ticker), true)}
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
                            <li>
                                {@render result(p.company_ticker, p.image_url, p.name, `${p.brand_name} · ${p.company_name}`, betterOptions(p.product_type ? [p.product_type] : [], p.company_ticker), true)}
                            </li>
                        {/each}
                    </ul>
                </section>
            {:else if !brandResults.length && !companyResults.length}
                <p class="empty">No match for &ldquo;{query.trim()}&rdquo;.
                    {#if suggestion}Did you mean <button type="button" class="suggest" onclick={() => query = suggestion}>{suggestion}</button>?{/if}
                </p>
            {/if}
        {:else}
            <section class="landing">
                <h2>Each aisle, best grades first</h2>
                {#each topByCategory as c}
                    <div class="aisle">
                        <button type="button" class="aisle-name" onclick={() => category = c.category}>{categoryLabel(c.category)} &rsaquo;</button>
                        {#if c.type}<span class="aisle-type">{categoryLabel(c.type)}</span>{/if}
                        <div class="aisle-picks">
                            {#each c.picks as p}
                                {@const g = gradeOf(p.company_ticker)}
                                <a class="pick" href="{base}/company/{p.company_ticker}">
                                    <span class="thumb">{#if p.image_url}<img src={p.image_url} alt="" loading="lazy" />{/if}</span>
                                    <span class="pick-company">{p.company_name}</span>
                                    <span class="pick-product">{p.name}</span>
                                    <span class="pick-grade grade-badge {getGradeClass(g || '')}">{g}</span>
                                    <span class="pick-cov">{groupsByTicker[p.company_ticker]} of {groupCount} issues</span>
                                </a>
                            {/each}
                        </div>
                    </div>
                {/each}
                <p class="landing-note">Each row compares one kind of product where possible: up to {MAX_A_PER_CATEGORY} companies graded A, then one graded B or C, then one graded D or F. Companies graded on {MIN_ISSUES_PREFERRED} or more issues come first.</p>
            </section>
        {/if}
    {/if}
</div>

<style>
    /* Light palette for shoppers, in line with shopping and rating sites */
    :global(body.shop-light) {
        --bg-primary: #faf8f5;
        --bg-card: #ffffff;
        --bg-input: #ffffff;
        --border-color: #e2ddd6;
        --text-primary: #1c1917;
        --text-secondary: #44403c;
        --text-muted: #78716c;
        --accent: #0f766e;
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    :global(body.shop-light a) { color: var(--accent); }
    .shop-page { max-width: 1120px; margin: 0 auto; padding: 1rem 0 3rem; }
    .search input { max-width: 720px; }
    /* Masthead after the 2000 edition cover: green band, white condensed caps */
    .masthead {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: #2e8b4f;
        margin: -1rem -1rem 0;
        padding: 0.6rem 1rem;
    }
    .masthead h1 {
        margin: 0;
        font-family: "Oswald", "Arial Narrow", sans-serif;
        font-weight: 700;
        font-size: 1.35rem;
        line-height: 1.1;
        text-transform: uppercase;
        letter-spacing: 0.01em;
        color: #ffffff;
    }
    .masthead .home-link { color: #ffffff; font-size: 0.8rem; opacity: 0.9; flex-shrink: 0; }

    .search {
        position: sticky;
        top: 0;
        z-index: 2;
        background: var(--bg-primary);
        margin: 0 -1rem;
        padding: 0.6rem 1rem 0;
    }
    .search input {
        width: 100%;
        box-sizing: border-box;
        font-size: 1.05rem;
        padding: 0.6rem 0.85rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        background: var(--bg-input);
        color: var(--text-primary);
    }
    .search input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
    .visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

    .chips {
        display: flex;
        gap: 0.4rem;
        margin: 0.6rem -1rem 0;
        padding: 0 1rem 0.2rem;
        overflow-x: auto;
        scrollbar-width: none;
    }
    .chips::-webkit-scrollbar { display: none; }
    .chip {
        font: inherit;
        font-size: 0.85rem;
        min-height: 40px;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
        color: var(--text-secondary);
        cursor: pointer;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .chip:hover { border-color: var(--accent); }
    .chip.active { background: var(--accent); border-color: var(--accent); color: #ffffff; }

    .status { color: var(--text-muted); font-size: 0.85rem; min-height: 1.2em; margin: 1rem 0 0.25rem; }
    h2 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 1.25rem 0 0.4rem; }

    .results { list-style: none; margin: 0; padding: 0; }
    .results > li { border-top: 1px solid var(--border-color); }
    .row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.6rem 0.25rem;
        text-decoration: none;
        color: inherit;
    }
    .row:hover .name { color: var(--accent); }
    .main { display: flex; flex-direction: column; min-width: 0; }
    .name { font-weight: 600; }
    .owner { color: var(--text-muted); font-size: 0.85rem; }
    /* Letter on top, plain word underneath, so the product name keeps the width */
    .grade { display: flex; flex-direction: column-reverse; align-items: center; gap: 0.1rem; flex-shrink: 0; min-width: 56px; }
    .grade-word { color: var(--text-secondary); font-size: 0.72rem; white-space: nowrap; }
    .grade .grade-badge { font-size: 1.1rem; min-width: 44px; }
    .ungraded { color: var(--text-muted); font-size: 0.75rem; flex-shrink: 0; width: 56px; text-align: center; line-height: 1.2; }

    .thumb {
        width: 44px;
        height: 44px;
        flex-shrink: 0;
        border-radius: 0.35rem;
        background: #f1ede6;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .thumb img { max-width: 100%; max-height: 100%; object-fit: contain; }
    .main { flex: 1; }

    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; padding: 0.6rem 0; }
    .card {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        padding: 0.55rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        background: var(--bg-card);
        text-decoration: none;
        color: inherit;
        min-width: 0;
    }
    .card:hover .name { color: var(--accent); }
    .card-better { border-color: #2e8b4f; background: #f1f8f3; }
    .card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.4rem; margin-bottom: 0.15rem; }
    .card .name { font-size: 0.92rem; line-height: 1.25; }
    .card .owner { font-size: 0.78rem; line-height: 1.3; }
    .card .grade { min-width: 0; }
    .card .grade .grade-badge { font-size: 1rem; min-width: 40px; padding: 0.15rem 0.4rem; }
    .tag {
        position: absolute;
        top: -0.55rem;
        left: 0.5rem;
        background: #2e8b4f;
        color: #ffffff;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.05rem 0.4rem;
        border-radius: 0.25rem;
    }

    .landing h2 { margin-top: 0.5rem; }
    .aisle { padding: 0.5rem 0 0.75rem; border-top: 1px solid var(--border-color); }
    .aisle-name { font: inherit; font-weight: 700; color: var(--accent); background: none; border: none; padding: 0.2rem 0; cursor: pointer; }
    .aisle-type { color: var(--text-muted); font-size: 0.85rem; margin-left: 0.4rem; }
    .aisle-picks { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.5rem; margin-top: 0.35rem; }
    .pick {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
        padding: 0.5rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        background: var(--bg-card);
        text-decoration: none;
        color: inherit;
        min-width: 0;
    }
    .pick:hover .pick-company { color: var(--accent); }
    .pick-company { font-weight: 700; font-size: 0.85rem; line-height: 1.2; }
    .pick-product { font-size: 0.75rem; color: var(--text-muted); line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .pick-grade { align-self: flex-start; font-size: 0.95rem; min-width: 36px; padding: 0.1rem 0.35rem; margin-top: 0.2rem; }
    .pick-cov { font-size: 0.68rem; color: var(--text-muted); }
    .landing-note { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem; }

    /* Phones: each aisle is one row that scrolls sideways */
    @media (max-width: 599px) {
        .aisle-picks { display: flex; overflow-x: auto; margin: 0.35rem -1rem 0; padding: 0 1rem 0.25rem; scroll-snap-type: x proximity; scroll-padding-inline: 1rem; }
        .pick { flex: 0 0 140px; scroll-snap-align: start; }
    }

    /* Wide screens: results and aisles side by side in two columns */
    @media (min-width: 900px) {
        .results { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 2rem; }
    }

    .suggest { font: inherit; color: var(--accent); background: none; border: none; padding: 0; text-decoration: underline; cursor: pointer; }

    .empty { color: var(--text-secondary); margin-top: 1rem; }
    .error { color: #ef4444; }
</style>
