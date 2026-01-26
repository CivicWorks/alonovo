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

export interface Company {
    id: number;
    uri: string;
    ticker: string;
    name: string;
    sector: string;
    scores: CompanyScore[];
}
