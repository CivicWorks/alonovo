export function formatMoney(amount: number): string {
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
    return `$${(amount / 1000).toFixed(0)}K`;
}

export function getGradeClass(grade: string): string {
    return `grade-${grade.charAt(0)}`;
}
