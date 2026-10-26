<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchDealCategories, fetchDeals, fetchValues } from '$lib/api';
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

    onMount(async () => {
        document.body.classList.add('shop-light');
        try {
            const [cs, values] = await Promise.all([fetchCompanies(), fetchValues()]);
            const groupKey = new Map(values.map(v => [v.slug, v.display_group || v.slug]));
            groupCount = new Set(groupKey.values()).size;
            dealCategories = await fetchDealCategories().catch(() => []);
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
    <p class="lead">Know before you buy. Best-graded companies first.</p>

    <form class="search" role="search" onsubmit={search}>
        <label for="bf-q" class="visually-hidden">Brand, company or product</label>
        <input id="bf-q" type="search" placeholder="Apple, Nike, Best Buy…" bind:value={query} autocomplete="off" />
    </form>

    {#if loading}
        <p class="status">Loading&hellip;</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
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
    @media (min-width: 900px) {
        .list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 2rem; }
    }
</style>
