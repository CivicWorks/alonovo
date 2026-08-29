<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchValues } from '$lib/api';
    import { computeOverallGrade, getGradeClass } from '$lib/utils';
    import type { Company, ValueDef } from '$lib/types';

    let companies: Company[] = $state([]);
    let values: ValueDef[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    onMount(async () => {
        try {
            [companies, values] = await Promise.all([fetchCompanies(), fetchValues()]);
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load';
        } finally {
            loading = false;
        }
    });

    let constituents = $derived(
        companies
            .map(c => ({ company: c, grade: computeOverallGrade(c, values) }))
            .filter(x => x.grade !== null && x.grade.startsWith('A'))
            .sort((a, b) => a.company.name.localeCompare(b.company.name))
    );

    let disqualifyingValues = $derived(values.filter(v => v.is_disqualifying));
</script>

<svelte:head>
    <title>The Alonovo List</title>
</svelte:head>

<div class="list-page">
    <a href="{base}/" class="back-btn">&larr; Back to companies</a>

    <h1>The Alonovo List</h1>
    <p class="subtitle">Every company currently graded A across all Alonovo values. Regenerated from live data — constituents change as the evidence changes.</p>

    {#if loading}
        <p>Loading&hellip;</p>
    {:else if error}
        <p class="error">{error}</p>
    {:else}
        <p class="count"><strong>{constituents.length}</strong> constituents</p>

        <table class="constituents">
            <thead>
                <tr><th>Company</th><th>Ticker</th><th>Sector</th><th>Grade</th></tr>
            </thead>
            <tbody>
                {#each constituents as { company, grade }}
                    <tr>
                        <td>{#if company.ticker}<a href="{base}/company/{company.ticker}">{company.name}</a>{:else}{company.name}{/if}</td>
                        <td>{company.ticker || '—'}</td>
                        <td>{company.sector || '—'}</td>
                        <td><span class="grade-badge {getGradeClass(grade || '')}">{grade}</span></td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <section class="methodology">
            <h2>Methodology</h2>
            <p>A company is a constituent while its overall Alonovo grade is in the A range. The overall grade is the average of its grades across all Alonovo value groups, each group counting once.</p>
            <ul>
                <li><strong>Disqualifying override:</strong> an F on any disqualifying value
                    ({disqualifyingValues.map(v => v.name).join(', ')}) makes the overall grade F —
                    no amount of good behavior elsewhere compensates.</li>
                <li><strong>Grade scale:</strong> A &ge; 0.8 &middot; B &ge; 0.3 &middot; C &ge; &minus;0.1 &middot; D &ge; &minus;0.5 &middot; F below.</li>
                <li><strong>Every grade is traceable:</strong> click any company for the individual claims behind its grades, each with its source.</li>
            </ul>
            <p><a href="{base}/about">About Alonovo</a></p>
        </section>
    {/if}
</div>

<style>
    .list-page { max-width: 900px; margin: 0 auto; padding: 1rem 0 3rem; }
    .subtitle { color: var(--muted, #94a3b8); max-width: 42rem; }
    .count { margin: 1.25rem 0 0.5rem; }
    .constituents { width: 100%; border-collapse: collapse; }
    .constituents th { text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; padding: 0.4rem 0.6rem; }
    .constituents td { padding: 0.45rem 0.6rem; border-top: 1px solid rgba(148, 163, 184, 0.2); }
    .constituents a { text-decoration: none; }
    .constituents a:hover { text-decoration: underline; }
    .methodology { margin-top: 2.5rem; }
    .methodology ul { padding-left: 1.2rem; }
    .methodology li { margin: 0.4rem 0; }
    .error { color: #ef4444; }
</style>
