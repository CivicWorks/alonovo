import type { Company, ValueDef, ValueSnapshot } from './types';

export function formatMoney(amount: number): string {
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
    return `$${(amount / 1000).toFixed(0)}K`;
}

export function getGradeClass(grade: string): string {
    return `grade-${grade.charAt(0)}`;
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
