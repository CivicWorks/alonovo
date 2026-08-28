<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { fetchCompanies, fetchValues } from '$lib/api';
    import { getGradeClass, groupValues, buildFilterOptions, groupSlug } from '$lib/utils';
    import type { Company, ValueDef, ValueGroup } from '$lib/types';
    import UserMenu from '$lib/UserMenu.svelte';
    import ShareButtons from '$lib/ShareButtons.svelte';

    let companies: Company[] = $state([]);
    let values: ValueDef[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    onMount(async () => {
        try {
            [companies, values] = await Promise.all([fetchCompanies(), fetchValues()]);
        } catch (e) {
            error = 'Failed to load data';
        } finally {
            loading = false;
        }
    });

    const slug = $derived($page.params.slug);
    const options = $derived(buildFilterOptions(values));

    /** The group (or ungrouped value) this page is about, and an optional single sub-value focus */
    const target = $derived.by(() => {
        const group = options.find(o => o.slug === slug);
        if (group) return { group, child: null as null | { key: string; label: string; slug: string } };
        for (const o of options) {
            const child = o.children.find(c => c.slug === slug);
            if (child) return { group: o, child };
        }
        return null;
    });

    const groupValueDefs = $derived.by((): ValueDef[] => {
        if (!target) return [];
        const t = target;
        return values.filter(v => (v.display_group || v.slug) === t.group.key && (!t.child || v.slug === t.child.key));
    });

    /** Companies with a grade in this group, with their group entry */
    const rows = $derived.by(() => {
        if (!target) return [];
        const t = target;
        const out: { company: Company; group: ValueGroup }[] = [];
        for (const c of companies) {
            const groups = groupValues(values, c.value_snapshots || []);
            const g = groups.find(g => g.groupName === t.group.key || g.values.some(v => v.slug === t.group.key));
            if (!g) continue;
            if (t.child && !g.snapshots.some(s => s.value_slug === t.child!.key)) continue;
            out.push({ company: c, group: g });
        }
        return out.sort((a, b) => b.group.score - a.group.score || a.company.name.localeCompare(b.company.name));
    });

    const gradeCounts = $derived.by(() => {
        const counts: Record<string, number> = { A: 0, B: 0, C: 0, D: 0, F: 0 };
        for (const r of rows) {
            const letter = r.group.grade.charAt(0);
            if (letter in counts) counts[letter]++;
        }
        return counts;
    });

    /** Turn bare URLs in a description into links */
    function linkify(text: string): string {
        const esc = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return esc.replace(/https?:\/\/[^\s)]+/g, (u) => `<a href="${u}" target="_blank" rel="noreferrer">${u.replace(/^https?:\/\/(www\.)?/, '')}</a>`);
    }

    function snapFor(group: ValueGroup, valueSlug: string) {
        return group.snapshots.find(s => s.value_slug === valueSlug) || null;
    }
</script>

<svelte:head>
    <title>{target ? target.child ? target.child.label : target.group.label : 'Values'} — Alonovo</title>
</svelte:head>

<header class="detail-banner">
    <a href="{base}/" class="back-link">&larr; Alonovo</a>
    <div class="banner-right">
        <UserMenu />
    </div>
</header>

<div class="container">
    {#if loading}
        <div class="loading">Loading...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else if !target}
        <div class="error">No such value: {slug}</div>
    {:else}
        <div class="values-page">
            <div class="values-header">
                <div>
                    {#if target.child}
                        <div class="crumb"><a href="{base}/values/{target.group.slug}">{target.group.label}</a></div>
                    {/if}
                    <h2>{target.child ? target.child.label : target.group.label}</h2>
                    <div class="values-meta">
                        {rows.length} of {companies.length} companies graded
                    </div>
                </div>
                <div class="grade-dist">
                    {#each Object.entries(gradeCounts) as [letter, n]}
                        <span class="grade-count {getGradeClass(letter)}"><b>{letter}</b> {n}</span>
                    {/each}
                </div>
            </div>

            <ShareButtons url={typeof window !== 'undefined' ? window.location.href : ''} title={`${target.child ? target.child.label : target.group.label} on Alonovo`} />

            <details class="subvalues">
                <summary><h3>What is measured</h3></summary>
                {#each groupValueDefs as v}
                    {@const n = rows.filter(r => snapFor(r.group, v.slug)).length}
                    <div class="subvalue" id={v.slug}>
                        <div class="subvalue-head">
                            {#if target.group.children.length > 0 && !target.child}
                                <a class="subvalue-name" href="{base}/values/{v.slug}">{v.name}</a>
                            {:else}
                                <span class="subvalue-name">{v.name}</span>
                            {/if}
                            <span class="subvalue-count">{n} graded</span>
                            {#if v.is_disqualifying}<span class="badge badge-negative">disqualifying</span>{/if}
                        </div>
                        <p class="subvalue-desc">{@html linkify(v.description)}</p>
                    </div>
                {/each}
            </details>

            <section class="graded">
                <h3>Companies</h3>
                {#if rows.length === 0}
                    <p class="empty">No company has data for this yet.</p>
                {:else}
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Company</th>
                                    <th>Grade</th>
                                    {#each groupValueDefs as v}
                                        <th>{v.name}</th>
                                    {/each}
                                </tr>
                            </thead>
                            <tbody>
                                {#each rows as r}
                                    <tr>
                                        <td>
                                            <a href="{base}/company/{r.company.ticker || r.company.id}#{groupSlug(target.group.key)}">{r.company.name}</a>
                                            {#if r.company.ticker}<span class="ticker">{r.company.ticker}</span>{/if}
                                        </td>
                                        <td><span class="grade-pill {getGradeClass(r.group.grade)}">{r.group.grade}</span></td>
                                        {#each groupValueDefs as v}
                                            {@const s = snapFor(r.group, v.slug)}
                                            <td>
                                                {#if s}
                                                    <span class="grade-pill small {getGradeClass(s.grade)}">{s.grade}</span>
                                                    <span class="snap-text">{s.display_text}</span>
                                                {:else}
                                                    <span class="none">&mdash;</span>
                                                {/if}
                                            </td>
                                        {/each}
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                    <p class="hint">Click a company for the source of every number.</p>
                {/if}
            </section>
        </div>
    {/if}
</div>

<style>
    .values-page { padding: 1rem 0 3rem; }
    .values-page a, .values-page :global(.subvalue-desc a) { color: var(--accent); }
    .detail-banner { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; }
    .back-link { color: rgba(255,255,255,0.85); text-decoration: none; font-size: 0.9rem; font-weight: 600; }
    .back-link:hover { color: white; }
    .values-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
    .values-header h2 { margin: 0.25rem 0; }
    .crumb { font-size: 0.85rem; }
    .values-meta { color: var(--text-secondary); font-size: 0.9rem; }
    .grade-dist { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .grade-count { padding: 0.25rem 0.6rem; border-radius: 0.25rem; background: var(--color-surface-700); font-size: 0.85rem; }
    .grade-count.grade-A b { color: #4ade80; }
    .grade-count.grade-B b { color: #bbf004; }
    .grade-count.grade-C b { color: #facc15; }
    .grade-count.grade-D b { color: #fb923c; }
    .grade-count.grade-F b { color: #f87171; }
    section, .subvalues { margin-top: 1.5rem; }
    .subvalues > summary { cursor: pointer; }
    .subvalues > summary h3 { display: inline; margin-left: 0.25rem; }
    h3 { margin-bottom: 0.75rem; }
    .subvalue { padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 0.25rem; margin-bottom: 0.5rem; background: var(--bg-card); scroll-margin-top: 1rem; }
    .subvalue-head { display: flex; gap: 0.75rem; align-items: baseline; flex-wrap: wrap; }
    .subvalue-name { font-weight: 700; }
    .subvalue-count { color: var(--text-secondary); font-size: 0.85rem; }
    .subvalue-desc { margin: 0.4rem 0 0; color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; word-break: break-word; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border-color); vertical-align: top; }
    th { color: var(--text-secondary); font-weight: 600; font-size: 0.8rem; white-space: nowrap; }
    .ticker { color: var(--text-secondary); font-size: 0.8rem; margin-left: 0.4rem; }
    .grade-pill { display: inline-block; min-width: 2rem; text-align: center; padding: 0.15rem 0.4rem; border-radius: 0.25rem; font-weight: 700; color: white; }
    .grade-pill.small { min-width: 1.6rem; font-size: 0.8rem; }
    .grade-pill.grade-A { background: #22c55e; }
    .grade-pill.grade-B { background: #84cc16; }
    .grade-pill.grade-C { background: #eab308; color: #1a1a1a; }
    .grade-pill.grade-D { background: #f97316; }
    .grade-pill.grade-F { background: #ef4444; }
    .snap-text { margin-left: 0.4rem; color: var(--text-secondary); font-size: 0.85rem; }
    .none { color: var(--text-secondary); }
    .empty, .hint { color: var(--text-secondary); font-size: 0.9rem; }
</style>
