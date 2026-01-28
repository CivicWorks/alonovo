import type { Company, ValueDef, ValueSnapshot, CategorySnapshot } from './types';
import { CATEGORIES } from './categories';

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

export function rollUpToCategories(snapshots: ValueSnapshot[]): CategorySnapshot[] {
    if (!snapshots || snapshots.length === 0) return [];

    const result: CategorySnapshot[] = [];

    for (const cat of CATEGORIES) {
        if (cat.valueSlugs.length === 0) continue;

        const matching = snapshots.filter(s => cat.valueSlugs.includes(s.value_slug));
        if (matching.length === 0) continue;

        const avg = matching.reduce((sum, s) => sum + s.score, 0) / matching.length;

        result.push({
            categorySlug: cat.slug,
            categoryName: cat.name,
            score: avg,
            grade: scoreToGrade(avg),
            isDisqualifying: !!cat.isDisqualifying,
            snapshots: matching,
        });
    }

    return result;
}

export function computeOverallGrade(company: Company, values: ValueDef[]): string | null {
    const snaps = company.value_snapshots;
    if (!snaps || snaps.length === 0) return null;

    // Build lookup of disqualifying values
    const disqualifying = new Set(values.filter(v => v.is_disqualifying).map(v => v.slug));

    // If any disqualifying value has F grade, overall is F
    for (const snap of snaps) {
        if (disqualifying.has(snap.value_slug) && snap.grade.startsWith('F')) {
            return 'F';
        }
    }

    // Average scores, map to grade
    const avg = snaps.reduce((sum, s) => sum + s.score, 0) / snaps.length;
    if (avg >= 0.8) return 'A';
    if (avg >= 0.3) return 'B';
    if (avg >= -0.1) return 'C';
    if (avg >= -0.5) return 'D';
    return 'F';
}
