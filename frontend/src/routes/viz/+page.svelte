<script lang="ts">
    import { base } from '$app/paths';
    import { onMount } from 'svelte';
    import { fetchCompanies, fetchValues } from '$lib/api';
    import { computeOverallGrade, groupValues } from '$lib/utils';
    import type { Company, ValueDef } from '$lib/types';
    import { Chart, BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

    Chart.register(BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

    let companies: Company[] = $state([]);
    let values: ValueDef[] = $state([]);
    let loading = $state(true);
    let error = $state('');

    let gradeCanvas = $state<HTMLCanvasElement>(undefined as any);
    let sectorCanvas = $state<HTMLCanvasElement>(undefined as any);
    let gradeChart: Chart | null = null;
    let sectorChart: Chart | null = null;

    onMount(() => {
        const init = async () => {
            try {
                [companies, values] = await Promise.all([
                    fetchCompanies(),
                    fetchValues(),
                ]);
                loading = false;

                // Wait for DOM update
                await new Promise(r => setTimeout(r, 0));
                renderGradeChart();
                renderSectorChart();
            } catch (e) {
                error = 'Failed to load data';
                loading = false;
            }
        };
        init();

        return () => {
            gradeChart?.destroy();
            sectorChart?.destroy();
        };
    });

    function renderGradeChart() {
        const counts: Record<string, number> = { A: 0, B: 0, C: 0, D: 0, F: 0 };
        for (const c of companies) {
            const grade = computeOverallGrade(c, values);
            if (grade) {
                const letter = grade.charAt(0);
                if (letter in counts) counts[letter]++;
            }
        }

        gradeChart = new Chart(gradeCanvas, {
            type: 'bar',
            data: {
                labels: ['A', 'B', 'C', 'D', 'F'],
                datasets: [{
                    label: 'Number of Companies',
                    data: [counts.A, counts.B, counts.C, counts.D, counts.F],
                    backgroundColor: ['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444'],
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Grade Distribution', font: { size: 18 }, color: '#1a5f2a' },
                    legend: { display: false },
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                },
            },
        });
    }

    function renderSectorChart() {
        const sectorScores: Record<string, { total: number; count: number }> = {};
        for (const c of companies) {
            if (!c.sector) continue;
            const groups = groupValues(values, c.value_snapshots || []);
            if (groups.length === 0) continue;
            const avg = groups.reduce((sum, g) => sum + g.score, 0) / groups.length;

            if (!sectorScores[c.sector]) sectorScores[c.sector] = { total: 0, count: 0 };
            sectorScores[c.sector].total += avg;
            sectorScores[c.sector].count++;
        }

        const sectors = Object.entries(sectorScores)
            .map(([name, { total, count }]) => ({ name, avg: total / count }))
            .filter(s => s.avg !== 0 || sectorScores[s.name].count > 0)
            .sort((a, b) => b.avg - a.avg);

        const colors = sectors.map(s => {
            if (s.avg >= 0.8) return '#22c55e';
            if (s.avg >= 0.3) return '#84cc16';
            if (s.avg >= -0.1) return '#eab308';
            if (s.avg >= -0.5) return '#f97316';
            return '#ef4444';
        });

        sectorChart = new Chart(sectorCanvas, {
            type: 'bar',
            data: {
                labels: sectors.map(s => s.name),
                datasets: [{
                    label: 'Average Score',
                    data: sectors.map(s => parseFloat(s.avg.toFixed(2))),
                    backgroundColor: colors,
                    borderRadius: 6,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Average Score by Sector', font: { size: 18 }, color: '#1a5f2a' },
                    legend: { display: false },
                },
                scales: {
                    x: { min: -1, max: 1 },
                },
            },
        });
    }
</script>

<header class="viz-banner">
    <a href="{base}/" class="back-link">&larr; Alonovo</a>
    <h1 class="viz-title">Data Visualizations</h1>
    <div></div>
</header>

<div class="container">
    {#if loading}
        <div class="loading">Loading data...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else}
        <div class="chart-card">
            <canvas bind:this={gradeCanvas}></canvas>
        </div>
        <div class="chart-card">
            <canvas bind:this={sectorCanvas}></canvas>
        </div>
    {/if}
</div>

<style>
    .viz-banner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(135deg, #1a5f2a 0%, #2d8a3e 100%);
        color: white;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
    }

    .back-link {
        color: rgba(255,255,255,0.85);
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .back-link:hover {
        color: white;
    }

    .viz-title {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .chart-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
</style>
