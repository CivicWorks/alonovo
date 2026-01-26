<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { fetchCompany } from '$lib/api';
    import { formatMoney } from '$lib/utils';
    import type { Company } from '$lib/types';

    let company: Company | null = $state(null);
    let loading = $state(true);
    let error = $state('');

    onMount(async () => {
        try {
            const ticker = $page.params.ticker;
            company = await fetchCompany(ticker);
        } catch (e) {
            error = 'Failed to load company';
        } finally {
            loading = false;
        }
    });
</script>

<a href="/" class="back-btn">← Back</a>

{#if loading}
    <div class="loading">Loading...</div>
{:else if error}
    <div class="error">{error}</div>
{:else if company}
    {@const score = company.scores[0]}
    <div class="company-detail">
        <h2>{company.name} ({company.ticker})</h2>
        <p><strong>Sector:</strong> {company.sector}</p>
        {#if score}
            <p><strong>Lobbying spend (2024):</strong> {formatMoney(score.raw_value)}</p>
            <p><strong>Grade:</strong> {score.grade}</p>
            <p><strong>Reason:</strong> {score.reason}</p>
        {/if}
        <section>
            <h3>How the grade is calculated</h3>
            <p>The grade is based solely on lobbying activities. Lower spending = better grade.</p>
            <ul>
                <li>Total lobbying expenditures</li>
                <li>Frequency and type of lobbying</li>
                <li>Organizations involved</li>
            </ul>
        </section>
    </div>
{/if}
