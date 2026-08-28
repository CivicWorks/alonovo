import type { Company, ValueDef, ValueSnapshot, ValueGroup } from './types';

export function formatMoney(amount: number): string {
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
    return `$${(amount / 1000).toFixed(0)}K`;
}

export function getGradeClass(grade: string): string {
    return `grade-${grade.charAt(0)}`;
}

export function scoreToGrade(score: number): string {
    if (score >= 0.8) {
        if (score >= 0.933) return 'A+';
        if (score >= 0.867) return 'A';
        return 'A-';
    }
    if (score >= 0.3) {
        if (score >= 0.633) return 'B+';
        if (score >= 0.467) return 'B';
        return 'B-';
    }
    if (score >= -0.1) {
        if (score >= 0.167) return 'C+';
        if (score >= 0.033) return 'C';
        return 'C-';
    }
    if (score >= -0.5) {
        if (score >= -0.233) return 'D+';
        if (score >= -0.367) return 'D';
        return 'D-';
    }
    return 'F';
}

/**
 * Group value snapshots by display_group.
 * Values with the same display_group collapse into one group.
 * Values with empty display_group become their own single-value group.
 */
export function groupValues(values: ValueDef[], snapshots: ValueSnapshot[], weights?: Record<string, number>): ValueGroup[] {
    if (!snapshots || snapshots.length === 0) return [];

    const valMap = new Map(values.map(v => [v.slug, v]));
    const groupMap = new Map<string, { snapshots: ValueSnapshot[]; values: ValueDef[] }>();

    for (const snap of snapshots) {
        const valDef = valMap.get(snap.value_slug);
        if (!valDef) continue;

        // Weight 0 excludes non-fixed values entirely
        if (weights && !valDef.is_fixed) {
            const w = weights[snap.value_slug];
            if (w !== undefined && w === 0) continue;
        }

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
        // Otherwise (weighted) average the sub-value scores
        let grade: string;
        let score: number;

        const hasDisqualifyingF = entry.snapshots.some(s => {
            const v = valMap.get(s.value_slug);
            return v?.is_disqualifying && s.grade.startsWith('F');
        });

        if (hasDisqualifyingF) {
            grade = 'F';
            score = -1;
        } else if (weights) {
            let weightedSum = 0;
            let totalWeight = 0;
            for (const s of entry.snapshots) {
                const v = valMap.get(s.value_slug);
                const w = v?.is_fixed ? 5 : (weights[s.value_slug] ?? 5);
                weightedSum += s.score * w;
                totalWeight += w;
            }
            score = totalWeight > 0 ? weightedSum / totalWeight : 0;
            grade = scoreToGrade(score);
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
export function computeOverallGrade(company: Company, values: ValueDef[], weights?: Record<string, number>): string | null {
    const snaps = company.value_snapshots;
    if (!snaps || snaps.length === 0) return null;

    const groups = groupValues(values, snaps, weights);
    if (groups.length === 0) return null;

    // If any group with disqualifying values is F, overall is F
    for (const g of groups) {
        if (g.isDisqualifying && g.grade === 'F') return 'F';
    }

    if (weights) {
        // Weighted average across groups; group weight = max weight of its values
        const valMap = new Map(values.map(v => [v.slug, v]));
        let weightedSum = 0;
        let totalWeight = 0;
        for (const g of groups) {
            let groupWeight = 0;
            for (const v of g.values) {
                const w = v.is_fixed ? 5 : (weights[v.slug] ?? 5);
                groupWeight = Math.max(groupWeight, w);
            }
            weightedSum += g.score * groupWeight;
            totalWeight += groupWeight;
        }
        const avg = totalWeight > 0 ? weightedSum / totalWeight : 0;
        return scoreToGrade(avg);
    }

    // Flat average across group scores
    const avg = groups.reduce((sum, g) => sum + g.score, 0) / groups.length;
    return scoreToGrade(avg);
}


/** URL slug for a display group or value name, e.g. "Worker Rights" -> "worker-rights" */
export function groupSlug(name: string): string {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

export interface FilterOption {
    key: string;        // display_group name or value slug (what the filter matches on)
    label: string;
    order: number;
    slug: string;       // URL slug for /values/<slug>
    children: { key: string; label: string; slug: string }[];  // sub-values of a group
}

/** Build filter options from value definitions: one entry per display_group (with its sub-values) or per ungrouped value */
export function buildFilterOptions(values: ValueDef[]): FilterOption[] {
    const map = new Map<string, FilterOption>();
    for (const v of values) {
        const key = v.display_group || v.slug;
        if (!map.has(key)) {
            map.set(key, {
                key,
                label: v.display_group || v.name,
                order: v.display_group_order,
                slug: groupSlug(v.display_group || v.slug),
                children: [],
            });
        }
        if (v.display_group) {
            map.get(key)!.children.push({ key: v.slug, label: v.name, slug: v.slug });
        }
    }
    return [...map.values()].sort((a, b) => a.order - b.order || a.label.localeCompare(b.label));
}
