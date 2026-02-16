import type { Company, ValueDef, ValueSnapshot, ValueGroup } from './types';

export function formatMoney(amount: number): string {
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
    return `$${(amount / 1000).toFixed(0)}K`;
}

export function getGradeClass(grade: string): string {
    return `grade-${grade.charAt(0)}`;
}

export function scoreToGrade(score: number): string {
    if (score >= 0.8) return 'A';
    if (score >= 0.3) return 'B';
    if (score >= -0.1) return 'C';
    if (score >= -0.5) return 'D';
    return 'F';
}

/**
 * Group value snapshots by display_group.
 * Values with the same display_group collapse into one group.
 * Values with empty display_group become their own single-value group.
 */
export function groupValues(values: ValueDef[], snapshots: ValueSnapshot[]): ValueGroup[] {
    if (!snapshots || snapshots.length === 0) return [];

    const valMap = new Map(values.map(v => [v.slug, v]));
    const groupMap = new Map<string, { snapshots: ValueSnapshot[]; values: ValueDef[] }>();

    for (const snap of snapshots) {
        const valDef = valMap.get(snap.value_slug);
        if (!valDef) continue;

        // Key: display_group if set, otherwise the slug itself (ungrouped)
        const key = valDef.display_group || snap.value_slug;

        if (!groupMap.has(key)) {
            groupMap.set(key, { snapshots: [], values: [] });
        }
        const entry = groupMap.get(key)!;
        entry.snapshots.push(snap);
        if (!entry.values.some(v => v.slug === valDef.slug)) {
            entry.values.push(valDef);
        }
    }

    const groups: ValueGroup[] = [];

    for (const [key, entry] of groupMap) {
        const isGrouped = entry.values.length > 0 && entry.values[0].display_group !== '';
        const groupName = isGrouped ? key : entry.values[0]?.name || key;
        const order = entry.values[0]?.display_group_order || 0;
        const isDisqualifying = entry.values.some(v => v.is_disqualifying);

        // Group grade: if any disqualifying sub-value is F, group is F
        // Otherwise average the sub-value scores
        let grade: string;
        let score: number;

        const hasDisqualifyingF = entry.snapshots.some(s => {
            const v = valMap.get(s.value_slug);
            return v?.is_disqualifying && s.grade.startsWith('F');
        });

        if (hasDisqualifyingF) {
            grade = 'F';
            score = -1;
        } else {
            score = entry.snapshots.reduce((sum, s) => sum + s.score, 0) / entry.snapshots.length;
            grade = scoreToGrade(score);
        }

        groups.push({ groupName, grade, score, isDisqualifying, order, snapshots: entry.snapshots, values: entry.values });
    }

    groups.sort((a, b) => a.order - b.order);
    return groups;
}

/**
 * Overall grade: average across groups (not individual values).
 * Each group counts once regardless of how many sub-values it has.
 * If any disqualifying value has F, overall is F.
 */
export function computeOverallGrade(company: Company, values: ValueDef[]): string | null {
    const snaps = company.value_snapshots;
    if (!snaps || snaps.length === 0) return null;

    const groups = groupValues(values, snaps);
    if (groups.length === 0) return null;

    // If any group with disqualifying values is F, overall is F
    for (const g of groups) {
        if (g.isDisqualifying && g.grade === 'F') return 'F';
    }

    // Average across group scores
    const avg = groups.reduce((sum, g) => sum + g.score, 0) / groups.length;
    return scoreToGrade(avg);
}
