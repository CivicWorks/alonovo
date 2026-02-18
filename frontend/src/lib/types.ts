export interface CompanyScore {
    id: number;
    score: number;
    grade: string;
    raw_value: number;
    reason: string;
    computed_at: string;
    source_claim_uris: string[];
    company: number;
}

export interface ValueSnapshot {
    value_slug: string;
    value_name: string;
    score: number;
    grade: string;
    highlight_on_card: boolean;
    highlight_priority: number;
    display_text: string;
    display_icon: string;
    computed_at: string;
}

export interface Badge {
    label: string;
    type: 'positive' | 'negative' | 'neutral';
    priority: number;
}

export interface Company {
    id: number;
    uri: string;
    ticker: string;
    name: string;
    sector: string;
    scores: CompanyScore[];
    badges?: Badge[];
    value_snapshots?: ValueSnapshot[];
}

export interface ClaimData {
    uri: string;
    subject: string;
    claim_type: string;
    amt: string | null;
    unit: string;
    label: string;
    effective_date: string | null;
    source_uri: string;
    how_known: string;
    statement: string;
    created_at: string;
}

export interface ValueDef {
    slug: string;
    name: string;
    description: string;
    value_type: string;
    is_fixed: boolean;
    is_disqualifying: boolean;
    min_weight: number;
    display_group: string;
    display_group_order: number;
    card_display_template: string;
    card_icon: string;
}

export interface ValueGroup {
    groupName: string;
    grade: string;
    score: number;
    isDisqualifying: boolean;
    order: number;
    snapshots: ValueSnapshot[];
    values: ValueDef[];
}

export interface User {
    id: number;
    email: string;
    username: string;
    is_staff: boolean;
    is_superuser: boolean;
}
