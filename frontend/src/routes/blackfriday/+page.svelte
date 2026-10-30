<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchDealCategories, fetchDeals, fetchDealsFromSource, fetchValues } from '$lib/api';
    import type { Deal } from '$lib/api';
    import { computeOverallGrade, getGradeClass } from '$lib/utils';
    import type { Company } from '$lib/types';
    import { BLACK_FRIDAY_SECTIONS } from '$lib/blackfriday';

    // Plain-word meaning of each letter, from the Alonovo grading table
    const GRADE_WORDS: Record<string, string> = { A: 'Very good', B: 'Good', C: 'Fair', D: 'Poor', F: 'Avoid' };
    const FINE_GRADES = ['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'];

    let rows: { company: Company; grade: string | null; issues: number }[] = $state([]);
    let groupCount = $state(0);
    let loading = $state(true);
    let error = $state('');
    let query = $state('');
    let dealCategories: {category: string, count: number}[] = $state([]);
    let dealCategory = $state('');
    let deals: Deal[] = $state([]);
    let gradeByTicker: Record<string, string | null> = $state({});
    const DEALS_SHOWN = 12;

    // Small makers from the Cause-Cart marketplace; links are tagged so Cause-Cart can count orders from here
    const MAKERS_SOURCE = 'cause_cart';
    const MAKERS_HOME = 'https://cause-cart.com/';
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
    let makers: Deal[] = $state([]);
    let makerCategory = $state('');
    let makerLabel = $state('');
    let makerBand = $state('');

    onMount(async () => {
        document.body.classList.add('shop-light');
        try {
            const [cs, values] = await Promise.all([fetchCompanies(), fetchValues()]);
            const groupKey = new Map(values.map(v => [v.slug, v.display_group || v.slug]));
            groupCount = new Set(groupKey.values()).size;
            dealCategories = await fetchDealCategories().catch(() => []);
            makers = await fetchDealsFromSource(MAKERS_SOURCE).catch(() => []);
            if (dealCategories.length) dealCategory = dealCategories[0].category;
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

    $effect(() => {
        gradeByTicker = Object.fromEntries(rows.map(r => [r.company.ticker, r.grade]));
    });

    $effect(() => {
        const c = dealCategory;
        if (c) fetchDeals(c).then(d => { if (c === dealCategory) deals = d; }).catch(() => { deals = []; });
    });

    function percentOff(d: Deal): number {
        const p = Number(d.price), r = Number(d.regular_price);
        return p && r && r > p ? Math.round((1 - p / r) * 100) : 0;
    }

    // Best-graded maker first, then the biggest discount; affiliate links play no part
    let shownDeals = $derived([...deals]
        .sort((a, b) => rank(gradeByTicker[b.company_ticker || ''] ?? null) - rank(gradeByTicker[a.company_ticker || ''] ?? null)
            || percentOff(b) - percentOff(a))
        .slice(0, DEALS_SHOWN));

    function checked(iso: string): string {
        return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
    }

    function rank(g: string | null): number {
        return g ? FINE_GRADES.indexOf(g) + 1 : 0;
    }

    let sections = $derived(BLACK_FRIDAY_SECTIONS.map(s => ({
        ...s,
        companies: rows
            .filter(r => s.tickers.includes(r.company.ticker))
            .sort((a, b) => rank(b.grade) - rank(a.grade) || b.issues - a.issues || a.company.name.localeCompare(b.company.name)),
    })).filter(s => s.companies.length));

    function count(values: string[]): string[] {
        const n = new Map<string, number>();
        values.forEach(v => n.set(v, (n.get(v) || 0) + 1));
        return [...n.keys()].sort((a, b) => n.get(b)! - n.get(a)! || a.localeCompare(b));
    }

    let makerCategories = $derived(count(makers.map(m => m.category).filter(Boolean)));
    let makerLabels = $derived(count(makers.flatMap(m => m.labels || [])));
    let shownMakers = $derived(makers.filter(m => {
        const band = PRICE_BANDS.find(b => b.label === makerBand);
        const p = Number(m.price);
        return (!makerCategory || m.category === makerCategory)
            && (!makerLabel || (m.labels || []).includes(makerLabel))
            && (!band || (p >= band.min && p < band.max));
    }));
    // Six photos for the top of the page, spread across sellers
    let heroPhotos = $derived.by(() => {
        const withPhoto = makers.filter(m => m.image_url);
        const firstPerSeller = withPhoto.filter((m, i) => withPhoto.findIndex(o => o.brand_name === m.brand_name) === i);
        return [...firstPerSeller, ...withPhoto.filter(m => !firstPerSeller.includes(m))].slice(0, 6);
    });

    function tagged(url: string): string {
        return url + (url.includes('?') ? '&' : '?') + CAMPAIGN;
    }

    function search(e: Event) {
        e.preventDefault();
        if (query.trim()) window.location.href = `${base}/shop?q=${encodeURIComponent(query.trim())}`;
    }
</script>

<svelte:head>
    <title>Black Friday — Alonovo</title>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
</svelte:head>

<div class="bf-page">
    <header class="masthead">
        <h1>Black Friday</h1>
        <a href="{base}/" class="home-link">Alonovo</a>
    </header>
    <!-- Headline: the project owner's ad copy. Lead, section subtitles and the Cause-Cart fine print are AI-written: replace with the team's own words. -->
    <section class="hero">
        <div class="hero-text">
            <h2 class="hero-title">Feel good about your Black Friday binge.</h2>
            <p class="lead">Know before you buy. Gifts from small makers who do good, and the best-graded big brands first.</p>
            <ul class="days">
                {#each DAYS as d}<li><strong>{d.day}</strong> {d.name}</li>{/each}
            </ul>
            <form class="search" role="search" onsubmit={search}>
                <label for="bf-q" class="visually-hidden">Brand, company or product</label>
                <input id="bf-q" type="search" placeholder="Look up a brand: Apple, Nike, Best Buy…" bind:value={query} autocomplete="off" />
            </form>
            <nav class="jumps" aria-label="On this page">
                {#if makers.length}<a href="#makers">Gifts from small makers</a>{/if}
                <a href="#big-buys">Big buys, best grade first</a>
            </nav>
        </div>
        {#if heroPhotos.length >= 3}
            <div class="mosaic" aria-hidden="true">
                {#each heroPhotos as m}<img src={m.image_url} alt="" loading="eager" />{/each}
            </div>
        {/if}
    </section>

    {#if loading}
        <p class="status">Loading&hellip;</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        {#if makers.length}
            <section id="makers" class="makers">
                <h2 class="section-title">Gifts from small makers</h2>
                <p class="section-sub">Handmade, women-owned, Indigenous-owned and more, from sellers reviewed by <a href={tagged(MAKERS_HOME)} rel="noopener" target="_blank">Cause-Cart</a>.</p>
                <div class="filters">
                    <div class="chips" role="group" aria-label="What">
                        <button type="button" class="chip" class:active={!makerCategory} aria-pressed={!makerCategory} onclick={() => makerCategory = ''}>Everything</button>
                        {#each makerCategories as c}
                            <button type="button" class="chip" class:active={makerCategory === c} aria-pressed={makerCategory === c} onclick={() => makerCategory = makerCategory === c ? '' : c}>{c}</button>
                        {/each}
                    </div>
                    <div class="chips" role="group" aria-label="Price">
                        {#each PRICE_BANDS as b}
                            <button type="button" class="chip" class:active={makerBand === b.label} aria-pressed={makerBand === b.label} onclick={() => makerBand = makerBand === b.label ? '' : b.label}>{b.label}</button>
                        {/each}
                    </div>
                    {#if makerLabels.length}
                        <div class="chips" role="group" aria-label="Values">
                            {#each makerLabels as l}
                                <button type="button" class="chip value" class:active={makerLabel === l} aria-pressed={makerLabel === l} onclick={() => makerLabel = makerLabel === l ? '' : l}>{l}</button>
                            {/each}
                        </div>
                    {/if}
                </div>
                {#if shownMakers.length}
                    <ul class="cards">
                        {#each shownMakers as m}
                            <li>
                                <a class="maker" href={tagged(m.url)} rel="noopener" target="_blank">
                                    <span class="photo">{#if m.image_url}<img src={m.image_url} alt="" loading="lazy" />{/if}</span>
                                    {#if m.labels?.length}<span class="tags">{#each m.labels.slice(0, 2) as l}<span class="tag">{l}</span>{/each}</span>{/if}
                                    <span class="name">{m.title}</span>
                                    {#if m.brand_name}<span class="owner">by {m.brand_name}</span>{/if}
                                    {#if m.price}<span class="price"><strong>${Number(m.price).toFixed(2)}</strong></span>{/if}
                                </a>
                            </li>
                        {/each}
                    </ul>
                {:else}
                    <p class="status">Nothing matches all of those. <button type="button" class="linkish" onclick={() => { makerCategory = ''; makerLabel = ''; makerBand = ''; }}>Show everything</button></p>
                {/if}
                <p class="fine">Prices as listed on Cause-Cart; checkout happens there. Links tell Cause-Cart you came from Alonovo.</p>
            </section>
        {/if}

        {#if dealCategories.length}
            <section>
                <h2>Live deals</h2>
                <div class="chips">
                    {#each dealCategories as c}
                        <button type="button" class="chip" class:active={dealCategory === c.category} aria-pressed={dealCategory === c.category}
                            onclick={() => dealCategory = c.category}>{c.category}</button>
                    {/each}
                </div>
                <ul class="deals">
                    {#each shownDeals as d}
                        {@const g = gradeByTicker[d.company_ticker || ''] ?? null}
                        <li>
                            <a class="deal" href={d.affiliate_url || d.url} rel="sponsored noopener" target="_blank">
                                <span class="thumb">{#if d.image_url}<img src={d.image_url} alt="" loading="lazy" />{/if}</span>
                                <span class="main">
                                    <span class="name">{d.title}</span>
                                    <span class="price">
                                        {#if d.price}<strong>${d.price}</strong>{/if}
                                        {#if percentOff(d)}<s>${d.regular_price}</s> <span class="off">{percentOff(d)}% off</span>{/if}
                                    </span>
                                    <span class="owner">{d.company_name} · at {d.store_name} · price checked {checked(d.last_seen_at)}</span>
                                </span>
                                {#if g}<span class="grade"><span class="grade-badge {getGradeClass(g)}">{g}</span><span class="grade-word">{GRADE_WORDS[g.charAt(0)]}</span></span>{/if}
                            </a>
                        </li>
                    {/each}
                </ul>
                <p class="fine">Prices and stock can change; the store's price applies. Some links are affiliate links and may earn Alonovo a commission. They never change the order.</p>
            </section>
        {/if}

        <h2 id="big-buys" class="section-title">Big buys, best grade first</h2>
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
        <p class="more">Groceries and household goods: <a href="{base}/shop">Shopping for a Better World</a></p>
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
    .bf-page { max-width: 1120px; margin: 0 auto; padding: 1rem 0 3rem; }
    .masthead { display: flex; align-items: center; justify-content: space-between; gap: 1rem; background: #111; margin: -1rem -1rem 0; padding: 0.6rem 1rem; }
    .masthead h1 { margin: 0; font-family: "Oswald", "Arial Narrow", sans-serif; font-size: 1.35rem; text-transform: uppercase; color: #fff; }
    .masthead .home-link { color: #fff; font-size: 0.8rem; }
    .lead { color: var(--text-secondary); margin: 0.75rem 0 0.25rem; }
    .search input { width: 100%; max-width: 720px; box-sizing: border-box; font-size: 1.05rem; padding: 0.6rem 0.85rem; border-radius: 0.5rem; border: 1px solid var(--border-color); background: #fff; color: var(--text-primary); margin-top: 0.5rem; }
    .visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
    h2 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 1.5rem 0 0.4rem; }
    .list { list-style: none; margin: 0; padding: 0; }
    .list > li { border-top: 1px solid var(--border-color); }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; padding: 0.6rem 0.25rem; text-decoration: none; color: inherit; }
    .row:hover .name { color: var(--accent); }
    .main { display: flex; flex-direction: column; min-width: 0; }
    .name { font-weight: 600; }
    .owner { color: var(--text-muted); font-size: 0.8rem; }
    .grade { display: flex; flex-direction: column; align-items: center; gap: 0.1rem; flex-shrink: 0; min-width: 56px; }
    .grade .grade-badge { font-size: 1.05rem; min-width: 44px; }
    .grade-word { color: var(--text-secondary); font-size: 0.72rem; }
    .status { color: var(--text-muted); margin-top: 1rem; }
    .error { color: #ef4444; }
    .chips { display: flex; gap: 0.4rem; overflow-x: auto; padding-bottom: 0.2rem; scrollbar-width: none; }
    .chip { font: inherit; font-size: 0.85rem; min-height: 40px; padding: 0.3rem 0.85rem; border-radius: 999px; border: 1px solid var(--border-color); background: #fff; color: var(--text-secondary); cursor: pointer; white-space: nowrap; flex-shrink: 0; }
    .chip.active { background: var(--accent); border-color: var(--accent); color: #fff; }
    .deals { list-style: none; margin: 0.5rem 0 0; padding: 0; }
    .deals > li { border-top: 1px solid var(--border-color); }
    .deal { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.25rem; text-decoration: none; color: inherit; }
    .deal .main { flex: 1; }
    .thumb { width: 56px; height: 56px; flex-shrink: 0; border-radius: 0.35rem; background: #f1ede6; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .thumb img { max-width: 100%; max-height: 100%; object-fit: contain; }
    .price s { color: var(--text-muted); }
    .off { color: #b91c1c; font-weight: 600; font-size: 0.85rem; }
    .fine { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem; }
    .more { margin-top: 1.5rem; color: var(--text-secondary); }
    .hero { display: grid; gap: 1rem; margin: 0 -1rem; padding: 1.25rem 1rem 1.5rem; background: linear-gradient(160deg, #fff7e8 0%, #fdecef 55%, #e9f6f1 100%); }
    .hero-title { font-family: "Oswald", "Arial Narrow", sans-serif; font-size: clamp(1.9rem, 6vw, 3rem); line-height: 1.05; text-transform: none; letter-spacing: 0; color: #1c1917; margin: 0; }
    .hero .lead { font-size: 1.05rem; margin: 0.6rem 0 0.75rem; max-width: 36rem; }
    .days { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0 0 0.5rem; padding: 0; }
    .days li { background: #fff; border: 1px solid var(--border-color); border-radius: 999px; padding: 0.25rem 0.7rem; font-size: 0.8rem; color: var(--text-secondary); }
    .days strong { color: var(--text-primary); }
    .jumps { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
    .jumps a { display: inline-flex; align-items: center; min-height: 44px; padding: 0 1rem; border-radius: 999px; background: var(--accent); color: #fff !important; text-decoration: none; font-weight: 600; font-size: 0.95rem; }
    .jumps a + a { background: #fff; color: var(--accent) !important; border: 1px solid var(--accent); }
    .mosaic { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem; }
    .mosaic img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 0.6rem; background: #fff; }
    .section-title { font-family: "Oswald", "Arial Narrow", sans-serif; font-size: 1.5rem; text-transform: none; letter-spacing: 0; color: var(--text-primary); margin: 2rem 0 0.2rem; scroll-margin-top: 1rem; }
    .section-sub { color: var(--text-secondary); margin: 0 0 0.75rem; }
    .makers { scroll-margin-top: 1rem; }
    .filters { display: grid; gap: 0.4rem; margin-bottom: 0.75rem; }
    .chip.value { border-color: #f3c6d3; background: #fff5f8; }
    .chip.value.active { background: #be185d; border-color: #be185d; color: #fff; }
    .cards { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem 0.75rem; }
    .maker { display: flex; flex-direction: column; gap: 0.2rem; text-decoration: none; color: inherit; }
    .maker .photo { aspect-ratio: 1; border-radius: 0.6rem; overflow: hidden; background: #f1ede6; }
    .maker .photo img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s; }
    .maker:hover .photo img { transform: scale(1.03); }
    .maker:hover .name { color: var(--accent); }
    .maker .name { font-weight: 600; font-size: 0.92rem; line-height: 1.25; }
    .tags { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.3rem; }
    .tag { font-size: 0.68rem; font-weight: 600; color: #9d174d; background: #fce7f3; border-radius: 999px; padding: 0.1rem 0.45rem; }
    .linkish { font: inherit; background: none; border: 0; padding: 0; color: var(--accent); text-decoration: underline; cursor: pointer; }
    @media (min-width: 640px) {
        .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (min-width: 900px) {
        .hero { grid-template-columns: 1.1fr 1fr; align-items: center; padding: 2rem 1.5rem; border-radius: 0 0 1rem 1rem; }
        .cards { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    }
    @media (min-width: 900px) {
        .list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 2rem; }
    }
</style>
