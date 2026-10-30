<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchDealsFromSource, fetchValues } from '$lib/api';
    import type { Deal } from '$lib/api';
    import { computeOverallGrade, getGradeClass } from '$lib/utils';
    import type { Company } from '$lib/types';
    import { BLACK_FRIDAY_CATEGORIES, BLACK_FRIDAY_SECTIONS } from '$lib/blackfriday';

    // Plain-word meaning of each letter, from the Alonovo grading table
    const GRADE_WORDS: Record<string, string> = { A: 'Very good', B: 'Good', C: 'Fair', D: 'Poor', F: 'Avoid' };
    const FINE_GRADES = ['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'];

    // Products from the Cause-Cart marketplace; links are tagged so Cause-Cart can count orders from here
    const PRODUCTS_SOURCE = 'cause_cart';
    const CAUSE_CART_HOME = 'https://cause-cart.com/';
    const CAMPAIGN = 'utm_source=alonovo&utm_medium=referral&utm_campaign=blackfriday2026';
    const PRICE_BANDS = [
        { label: 'Under $25', min: 0, max: 25 },
        { label: '$25 to $50', min: 25, max: 50 },
        { label: 'Over $50', min: 50, max: Infinity },
    ];
    // Shopping days, Thanksgiving week 2026
    const DAYS = [
        { day: 'Fri Nov 27', name: 'Black Friday' },
        { day: 'Sat Nov 28', name: 'Small Business Saturday' },
        { day: 'Mon Nov 30', name: 'Cyber Monday' },
    ];
    const PRODUCTS_SHOWN = 12;

    let rows: { company: Company; grade: string | null; issues: number }[] = $state([]);
    let groupCount = $state(0);
    let loading = $state(true);
    let error = $state('');
    let query = $state('');
    let products: Deal[] = $state([]);
    let category = $state('');
    let label = $state('');
    let band = $state('');
    let showAll = $state(false);

    onMount(async () => {
        document.body.classList.add('shop-light');
        try {
            const [cs, values] = await Promise.all([fetchCompanies(), fetchValues()]);
            const groupKey = new Map(values.map(v => [v.slug, v.display_group || v.slug]));
            groupCount = new Set(groupKey.values()).size;
            products = await fetchDealsFromSource(PRODUCTS_SOURCE).catch(() => []);
            rows = cs.filter(c => c.ticker).map(c => ({
                company: c,
                grade: computeOverallGrade(c, values),
                issues: new Set((c.value_snapshots || []).map(s => groupKey.get(s.value_slug)).filter(Boolean)).size,
            }));
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load';
        } finally {
            loading = false;
        }
    });

    $effect(() => () => document.body.classList.remove('shop-light'));

    let gradeByTicker = $derived(Object.fromEntries(rows.map(r => [r.company.ticker, r.grade])));

    function rank(g: string | null): number {
        return g ? FINE_GRADES.indexOf(g) + 1 : 0;
    }

    function gradeOf(p: Deal): string | null {
        return p.company_ticker ? gradeByTicker[p.company_ticker] ?? null : null;
    }

    let words = $derived(query.trim().toLowerCase().split(/\s+/).filter(Boolean));
    function matches(...fields: (string | null | undefined)[]): boolean {
        const text = fields.filter(Boolean).join(' ').toLowerCase();
        return words.every(w => text.includes(w));
    }

    let current = $derived(BLACK_FRIDAY_CATEGORIES.find(c => c.name === category));

    function count(values: string[]): string[] {
        const n = new Map<string, number>();
        values.forEach(v => n.set(v, (n.get(v) || 0) + 1));
        return [...n.keys()].sort((a, b) => n.get(b)! - n.get(a)! || a.localeCompare(b));
    }
    let labels = $derived(count(products.flatMap(p => p.labels || [])));

    let shownProducts = $derived(products
        .filter(p => {
            const b = PRICE_BANDS.find(x => x.label === band);
            const price = Number(p.price);
            return (!current || current.deals.includes(p.category))
                && (!label || (p.labels || []).includes(label))
                && (!b || (price >= b.min && price < b.max))
                && matches(p.title, p.brand_name, p.category, ...(p.labels || []));
        })
        .sort((a, b) => rank(gradeOf(b)) - rank(gradeOf(a))));

    let sections = $derived(BLACK_FRIDAY_SECTIONS
        .filter(s => !current || current.sections.includes(s.title))
        .map(s => ({
            ...s,
            companies: rows
                .filter(r => s.tickers.includes(r.company.ticker) && matches(r.company.name, s.title))
                .sort((a, b) => rank(b.grade) - rank(a.grade) || b.issues - a.issues || a.company.name.localeCompare(b.company.name)),
        }))
        .filter(s => s.companies.length));

    let categoryCounts = $derived(Object.fromEntries(BLACK_FRIDAY_CATEGORIES.map(c => [c.name,
        products.filter(p => c.deals.includes(p.category)).length])));

    // Six photos for the top of the page, spread across sellers
    let heroPhotos = $derived.by(() => {
        const withPhoto = products.filter(p => p.image_url);
        const firstPerSeller = withPhoto.filter((p, i) => withPhoto.findIndex(o => o.brand_name === p.brand_name) === i);
        return [...firstPerSeller, ...withPhoto.filter(p => !firstPerSeller.includes(p))].slice(0, 6);
    });

    function tagged(url: string): string {
        return url + (url.includes('?') ? '&' : '?') + CAMPAIGN;
    }

    function pick(name: string) {
        category = category === name ? '' : name;
        showAll = false;
    }

    function clearAll() {
        category = ''; label = ''; band = ''; query = '';
    }

    function search(e: Event) {
        e.preventDefault();
        document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' });
    }
</script>

<svelte:head>
    <title>Shopping for a Better World: Black Friday — Alonovo</title>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
</svelte:head>

<div class="bf-page">
    <header class="masthead">
        <h1>Black Friday</h1>
        <a href="{base}/" class="home-link">Alonovo</a>
    </header>
    <!-- Headline: from the campaign brief. Lead and the "How it works" step titles are AI-written; step text reuses the earlier page's copy. Replace with the team's own words. -->
    <section class="hero">
        <div class="hero-text">
            <h2 class="hero-title">Shopping for a Better World</h2>
            <p class="lead">Find gifts from companies with better social and environmental practices. Know before you buy.</p>
            <form class="search" role="search" onsubmit={search}>
                <label for="bf-q" class="visually-hidden">What are you shopping for?</label>
                <input id="bf-q" type="search" placeholder="What are you shopping for?" bind:value={query} autocomplete="off" />
                <button type="submit">Search</button>
            </form>
            <ul class="days">
                {#each DAYS as d}<li><strong>{d.day}</strong> {d.name}</li>{/each}
            </ul>
            <a class="cta" href="#products">Explore products</a>
        </div>
        {#if heroPhotos.length >= 3}
            <div class="mosaic" aria-hidden="true">
                {#each heroPhotos as p}<img src={p.image_url} alt="" loading="eager" />{/each}
            </div>
        {/if}
    </section>

    <nav class="categories" aria-label="Categories">
        <button type="button" class="cat" class:active={!category} aria-pressed={!category} onclick={() => pick('')}>
            <span class="cat-name">Everything</span><span class="cat-count">{products.length || ''}</span>
        </button>
        {#each BLACK_FRIDAY_CATEGORIES as c}
            <button type="button" class="cat" class:active={category === c.name} aria-pressed={category === c.name} onclick={() => pick(c.name)}>
                <span class="cat-name">{c.name}</span><span class="cat-count">{categoryCounts[c.name] || (c.sections.length ? 'brands' : '')}</span>
            </button>
        {/each}
    </nav>

    {#if loading}
        <p class="status">Loading&hellip;</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <section id="products" class="products">
            <h2 class="section-title">{category || 'Featured'} products</h2>
            <p class="section-sub">Handmade, women-owned, Indigenous-owned and more, from sellers reviewed by <a href={tagged(CAUSE_CART_HOME)} rel="noopener" target="_blank">Cause-Cart</a>.</p>
            <div class="filters">
                <div class="chips" role="group" aria-label="Price">
                    {#each PRICE_BANDS as b}
                        <button type="button" class="chip" class:active={band === b.label} aria-pressed={band === b.label} onclick={() => band = band === b.label ? '' : b.label}>{b.label}</button>
                    {/each}
                </div>
                {#if labels.length}
                    <div class="chips" role="group" aria-label="Values">
                        {#each labels as l}
                            <button type="button" class="chip value" class:active={label === l} aria-pressed={label === l} onclick={() => label = label === l ? '' : l}>{l}</button>
                        {/each}
                    </div>
                {/if}
            </div>
            {#if shownProducts.length}
                <ul class="cards">
                    {#each showAll ? shownProducts : shownProducts.slice(0, PRODUCTS_SHOWN) as p}
                        {@const g = gradeOf(p)}
                        <li class="card">
                            <a class="photo" href={tagged(p.url)} rel="noopener" target="_blank" tabindex="-1" aria-hidden="true">
                                {#if p.image_url}<img src={p.image_url} alt="" loading="lazy" />{/if}
                            </a>
                            <div class="card-body">
                                {#if p.labels?.length}<span class="tags">{#each p.labels.slice(0, 2) as l}<span class="tag">{l}</span>{/each}</span>{/if}
                                <span class="name">{p.title}</span>
                                {#if p.brand_name}<span class="owner">by {p.brand_name}</span>{/if}
                                <div class="card-foot">
                                    {#if g}
                                        <span class="grade" title="Alonovo grade for {p.company_name}"><span class="grade-badge {getGradeClass(g)}">{g}</span><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span></span>
                                    {:else}
                                        <span class="grade" title="Alonovo has not graded this seller"><span class="grade-badge ungraded">–</span><span class="grade-word">Not graded</span></span>
                                    {/if}
                                    {#if p.price}<strong class="price">${Number(p.price).toFixed(2)}</strong>{/if}
                                </div>
                                <a class="shop" href={tagged(p.url)} rel="noopener" target="_blank">Shop now<span class="visually-hidden">: {p.title}</span></a>
                            </div>
                        </li>
                    {/each}
                </ul>
                {#if !showAll && shownProducts.length > PRODUCTS_SHOWN}
                    <button type="button" class="more-btn" onclick={() => showAll = true}>Show all {shownProducts.length}</button>
                {/if}
            {:else}
                <p class="status">
                    {#if current && !current.deals.length}No {current.name.toLowerCase()} products from Cause-Cart yet.{:else}Nothing matches all of those.{/if}
                    <button type="button" class="linkish" onclick={clearAll}>Show everything</button>
                    {#if query.trim()} or <a href="{base}/shop?q={encodeURIComponent(query.trim())}">look up “{query.trim()}” on Alonovo</a>{/if}
                </p>
            {/if}
            <p class="fine">Prices as listed on Cause-Cart; checkout happens there. Links tell Cause-Cart you came from Alonovo.</p>
        </section>

        {#if sections.length}
            <h2 id="big-buys" class="section-title">Big brands, best grade first</h2>
            <p class="section-sub">Graded on lobbying, CEO pay, carbon, how workers are treated and more. Tap a company to see why.</p>
            {#each sections as s}
                <section>
                    <h2>{s.title}</h2>
                    <ul class="list">
                        {#each s.companies as r}
                            {@const g = r.grade}
                            <li>
                                <a class="row" href="{base}/company/{r.company.ticker}">
                                    <span class="main">
                                        <span class="name">{r.company.name}</span>
                                        {#if r.issues}<span class="owner">graded on {r.issues} of {groupCount} issues</span>{/if}
                                    </span>
                                    {#if g}
                                        <span class="grade"><span class="grade-badge {getGradeClass(g)}">{g}</span><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span></span>
                                    {:else}
                                        <span class="grade"><span class="grade-word">Not graded yet</span></span>
                                    {/if}
                                </a>
                            </li>
                        {/each}
                    </ul>
                </section>
            {/each}
        {/if}

        <section class="how" aria-labelledby="how-title">
            <h2 id="how-title" class="section-title">How it works</h2>
            <ol class="steps">
                <li>
                    <strong>Alonovo grades companies</strong>
                    <span>A to F, on lobbying, CEO pay, carbon, how workers are treated and more. Tap a company to see why.</span>
                </li>
                <li>
                    <strong>Cause-Cart reviews small makers</strong>
                    <span>Handmade, women-owned, Indigenous-owned and more.</span>
                </li>
                <li>
                    <strong>You buy from the seller</strong>
                    <span>Checkout happens on Cause-Cart. Links tell Cause-Cart you came from Alonovo.</span>
                </li>
            </ol>
        </section>

        <section class="cta-band">
            <h2 class="section-title">Know before you buy.</h2>
            <div class="cta-row">
                <a class="cta" href="#products">Explore products</a>
                <a class="cta secondary" href="{base}/shop">Look up any brand</a>
            </div>
        </section>
    {/if}
</div>

<style>
    :global(body.shop-light) {
        --bg-primary: #faf8f5;
        --bg-card: #ffffff;
        --border-color: #e2ddd6;
        --text-primary: #1c1917;
        --text-secondary: #44403c;
        --text-muted: #78716c;
        --accent: #0f766e;
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    :global(body.shop-light a) { color: var(--accent); }
    :global(html) { scroll-behavior: smooth; }
    .bf-page { padding: 1rem 0 3rem; }
    .masthead { display: flex; align-items: center; justify-content: space-between; gap: 1rem; background: #111; margin: -1rem -1rem 0; padding: 0.6rem 1rem; }
    .masthead h1 { margin: 0; font-family: "Oswald", "Arial Narrow", sans-serif; font-size: 1.35rem; text-transform: uppercase; color: #fff; }
    .masthead .home-link { color: #fff; font-size: 0.8rem; }
    .visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
    h2 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 1.5rem 0 0.4rem; }

    /* Hero */
    .hero { display: grid; gap: 1.25rem; margin: 0 -1rem; padding: 1.75rem 1rem 2rem; background: linear-gradient(160deg, #fff7e8 0%, #fdecef 55%, #e9f6f1 100%); }
    .hero-title { font-family: "Oswald", "Arial Narrow", sans-serif; font-size: clamp(2.2rem, 7vw, 3.6rem); line-height: 1.02; text-transform: none; letter-spacing: 0; color: #1c1917; margin: 0; }
    .lead { color: var(--text-secondary); font-size: 1.1rem; margin: 0.75rem 0 1rem; max-width: 34rem; }
    .search { display: flex; max-width: 640px; background: #fff; border: 2px solid var(--accent); border-radius: 999px; overflow: hidden; box-shadow: 0 4px 18px rgba(15, 118, 110, 0.12); }
    .search input { flex: 1; min-width: 0; font: inherit; font-size: 1.1rem; padding: 0.85rem 1.1rem; border: 0; background: transparent; color: var(--text-primary); outline: none; }
    .search button { font: inherit; font-weight: 600; padding: 0 1.4rem; border: 0; background: var(--accent); color: #fff; cursor: pointer; }
    .days { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.9rem 0 1rem; padding: 0; }
    .days li { background: #fff; border: 1px solid var(--border-color); border-radius: 999px; padding: 0.25rem 0.7rem; font-size: 0.8rem; color: var(--text-secondary); }
    .days strong { color: var(--text-primary); }
    .cta { display: inline-flex; align-items: center; min-height: 48px; padding: 0 1.5rem; border-radius: 999px; background: var(--accent); color: #fff !important; text-decoration: none; font-weight: 600; font-size: 1rem; }
    .cta.secondary { background: #fff; color: var(--accent) !important; border: 1px solid var(--accent); }
    .mosaic { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
    .mosaic img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 0.75rem; background: #fff; }

    /* Categories */
    .categories { display: flex; gap: 0.5rem; overflow-x: auto; margin: 1.25rem 0 0; padding-bottom: 0.25rem; scrollbar-width: none; }
    .cat { flex: 1 0 auto; display: flex; flex-direction: column; align-items: flex-start; gap: 0.1rem; min-width: 104px; min-height: 64px; padding: 0.6rem 1rem; font: inherit; text-align: left; border-radius: 0.75rem; border: 1px solid var(--border-color); background: #fff; color: var(--text-primary); cursor: pointer; }
    .cat:hover { border-color: var(--accent); }
    .cat.active { background: var(--accent); border-color: var(--accent); color: #fff; }
    .cat-name { font-weight: 600; }
    .cat-count { font-size: 0.75rem; color: var(--text-muted); min-height: 1em; }
    .cat.active .cat-count { color: #d1fae5; }

    /* Products */
    .section-title { font-family: "Oswald", "Arial Narrow", sans-serif; font-size: 1.6rem; text-transform: none; letter-spacing: 0; color: var(--text-primary); margin: 2rem 0 0.2rem; scroll-margin-top: 1rem; }
    .section-sub { color: var(--text-secondary); margin: 0 0 0.75rem; }
    .products { scroll-margin-top: 1rem; }
    .filters { display: grid; gap: 0.4rem; margin-bottom: 1rem; }
    .chips { display: flex; gap: 0.4rem; overflow-x: auto; padding-bottom: 0.2rem; scrollbar-width: none; }
    .chip { font: inherit; font-size: 0.85rem; min-height: 40px; padding: 0.3rem 0.85rem; border-radius: 999px; border: 1px solid var(--border-color); background: #fff; color: var(--text-secondary); cursor: pointer; white-space: nowrap; flex-shrink: 0; }
    .chip.active { background: var(--accent); border-color: var(--accent); color: #fff; }
    .chip.value { border-color: #f3c6d3; background: #fff5f8; }
    .chip.value.active { background: #be185d; border-color: #be185d; color: #fff; }
    .cards { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
    .card { display: flex; flex-direction: column; background: #fff; border: 1px solid var(--border-color); border-radius: 0.85rem; overflow: hidden; transition: box-shadow 0.2s, transform 0.2s; }
    .card:hover { box-shadow: 0 8px 24px rgba(28, 25, 23, 0.08); transform: translateY(-2px); }
    .photo { display: block; aspect-ratio: 1; background: #f1ede6; overflow: hidden; }
    .photo img { width: 100%; height: 100%; object-fit: cover; }
    .card-body { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.65rem 0.75rem 0.75rem; flex: 1; }
    .name { font-weight: 600; font-size: 0.95rem; line-height: 1.25; }
    .owner { color: var(--text-muted); font-size: 0.8rem; }
    .tags { display: flex; flex-wrap: wrap; gap: 0.25rem; }
    .tag { font-size: 0.68rem; font-weight: 600; color: #9d174d; background: #fce7f3; border-radius: 999px; padding: 0.1rem 0.45rem; }
    .card-foot { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-top: auto; padding-top: 0.4rem; }
    .card-foot .grade { flex-direction: row; gap: 0.35rem; min-width: 0; }
    .card-foot .grade-badge { font-size: 0.9rem; min-width: 34px; padding: 0.15rem 0.35rem; }
    .price { font-size: 1rem; }
    .ungraded { background: #f1ede6; color: var(--text-muted); }
    .shop { display: flex; align-items: center; justify-content: center; min-height: 44px; margin-top: 0.5rem; border-radius: 999px; background: var(--accent); color: #fff !important; font-weight: 600; text-decoration: none; }
    .shop:hover { background: #115e59; }
    .more-btn { display: block; margin: 1rem auto 0; min-height: 44px; padding: 0 1.5rem; font: inherit; font-weight: 600; border-radius: 999px; border: 1px solid var(--accent); background: #fff; color: var(--accent); cursor: pointer; }
    .linkish { font: inherit; background: none; border: 0; padding: 0; color: var(--accent); text-decoration: underline; cursor: pointer; }
    .status { color: var(--text-muted); margin-top: 1rem; }
    .error { color: #ef4444; }
    .fine { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.75rem; }

    /* Graded companies */
    .list { list-style: none; margin: 0; padding: 0; }
    .list > li { border-top: 1px solid var(--border-color); }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; padding: 0.6rem 0.25rem; text-decoration: none; color: inherit; }
    .row:hover .name { color: var(--accent); }
    .main { display: flex; flex-direction: column; min-width: 0; }
    .grade { display: flex; flex-direction: column; align-items: center; gap: 0.1rem; flex-shrink: 0; min-width: 56px; }
    .grade .grade-badge { font-size: 1.05rem; min-width: 44px; }
    .grade-word { color: var(--text-secondary); font-size: 0.72rem; }

    /* How it works + closing call to action */
    .how { margin-top: 2.5rem; }
    .steps { list-style: none; counter-reset: step; margin: 0.75rem 0 0; padding: 0; display: grid; gap: 0.75rem; }
    .steps li { counter-increment: step; display: flex; flex-direction: column; gap: 0.25rem; padding: 1rem 1rem 1rem 3.25rem; position: relative; background: #fff; border: 1px solid var(--border-color); border-radius: 0.85rem; color: var(--text-secondary); }
    .steps li::before { content: counter(step); position: absolute; left: 1rem; top: 1rem; width: 1.6rem; height: 1.6rem; border-radius: 50%; background: var(--accent); color: #fff; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
    .steps strong { color: var(--text-primary); }
    .cta-band { margin: 2.5rem -1rem 0; padding: 1.75rem 1rem 2rem; text-align: center; background: linear-gradient(160deg, #e9f6f1 0%, #fff7e8 100%); }
    .cta-band .section-title { margin-top: 0; }
    .cta-row { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.6rem; margin-top: 0.75rem; }

    @media (min-width: 640px) {
        .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .steps { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (min-width: 900px) {
        .hero { grid-template-columns: 1.1fr 1fr; align-items: center; padding: 2.5rem 2rem; border-radius: 0 0 1rem 1rem; }
        .cards { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 2rem; }
        .cta-band { border-radius: 1rem; margin: 2.5rem 0 0; }
    }
    @media (min-width: 1200px) {
        .cards { grid-template-columns: repeat(5, minmax(0, 1fr)); }
    }
</style>
