import { base } from '$app/paths';
import type { BrandMapping, ClaimData, Company, Product, User, ValueDef } from './types';

function apiBase(): string {
    return `${base}/api`;
}

function siteBase(): string {
    return base;
}

export async function fetchCompanies(): Promise<Company[]> {
    const companies: Company[] = [];
    let url = `${apiBase()}/companies/`;
    while (url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch companies');
        }
        const data = await response.json();
        companies.push(...(data.results || data));
        url = data.next || '';
    }
    return companies;
}

export async function fetchCompany(ticker: string): Promise<Company> {
    const response = await fetch(`${apiBase()}/companies/${ticker}/`);
    if (!response.ok) {
        throw new Error('Failed to fetch company');
    }
    return response.json();
}

export async function fetchValues(): Promise<ValueDef[]> {
    const values: ValueDef[] = [];
    let url = `${apiBase()}/values/`;
    while (url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch values');
        }
        const data = await response.json();
        values.push(...(data.results || data));
        url = data.next || '';
    }
    return values;
}

export async function fetchCompanyClaims(ticker: string): Promise<ClaimData[]> {
    const response = await fetch(`${apiBase()}/companies/${ticker}/claims/`);
    if (!response.ok) {
        throw new Error('Failed to fetch claims');
    }
    return response.json();
}

export async function fetchCompaniesBySector(sector: string): Promise<Company[]> {
    const companies: Company[] = [];
    let url = `${apiBase()}/companies/?sector=${encodeURIComponent(sector)}`;
    while (url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch companies by sector');
        }
        const data = await response.json();
        companies.push(...(data.results || data));
        url = data.next || '';
    }
    return companies;
}

export async function fetchSectors(): Promise<string[]> {
    const response = await fetch(`${apiBase()}/sectors/`);
    if (!response.ok) {
        throw new Error('Failed to fetch sectors');
    }
    return response.json();
}

export async function fetchCurrentUser(): Promise<User | null> {
    try {
        const response = await fetch(`${apiBase()}/me/`, {
            credentials: 'include',
        });
        if (!response.ok) return null;
        const text = await response.text();
        if (!text) return null;
        return JSON.parse(text);
    } catch {
        return null;
    }
}

export async function fetchWeights(): Promise<{value_slug: string, weight: number}[]> {
    const response = await fetch(`${apiBase()}/me/weights/`, {
        credentials: 'include',
    });
    if (!response.ok) return [];
    return response.json();
}

export function getLoginUrl(): string {
    return `${base}/accounts/google/login/`;
}

export function getLogoutUrl(): string {
    return `${base}/accounts/logout/`;
}

export async function voteForCompany(ticker: string): Promise<{status: string, vote_count: number}> {
    const response = await fetch(`${apiBase()}/companies/${ticker}/vote/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
    });
    return response.json();
}

export async function fetchVoteLeaderboard(): Promise<{ticker: string, name: string, sector: string, vote_count: number}[]> {
    const response = await fetch(`${apiBase()}/votes/leaderboard/`);
    if (!response.ok) return [];
    return response.json();
}

export async function fetchProductCategories(): Promise<{category: string, count: number}[]> {
    const response = await fetch(`${apiBase()}/products/categories/`);
    if (!response.ok) {
        throw new Error('Failed to fetch product categories');
    }
    return response.json();
}

export async function fetchProductsByCategory(category: string): Promise<Product[]> {
    const response = await fetch(`${apiBase()}/products/?category=${encodeURIComponent(category)}`);
    if (!response.ok) {
        throw new Error('Failed to fetch products');
    }
    return response.json();
}

export async function fetchBrands(): Promise<BrandMapping[]> {
    const response = await fetch(`${apiBase()}/brands/`);
    if (!response.ok) {
        throw new Error('Failed to fetch brands');
    }
    return response.json();
}

export interface Deal {
    id: number;
    title: string;
    brand_name: string;
    company_name: string | null;
    company_ticker: string | null;
    store_name: string;
    store_ticker: string | null;
    category: string;
    price: string | null;
    regular_price: string | null;
    url: string;
    affiliate_url: string;
    image_url: string;
    last_seen_at: string;
}

export async function fetchDealCategories(): Promise<{category: string, count: number}[]> {
    const response = await fetch(`${apiBase()}/deals/categories/`);
    if (!response.ok) {
        throw new Error('Failed to fetch deal categories');
    }
    return response.json();
}

// Live deals in a category whose maker is a graded company, up to maxPages pages of 50
export async function fetchDeals(category: string, maxPages = 4): Promise<Deal[]> {
    const deals: Deal[] = [];
    let page = 1, pages = 1;
    while (page <= Math.min(pages, maxPages)) {
        const response = await fetch(`${apiBase()}/deals/?rated=1&category=${encodeURIComponent(category)}&page=${page}`);
        if (!response.ok) {
            throw new Error('Failed to fetch deals');
        }
        const data = await response.json();
        deals.push(...data.results);
        pages = data.pages;
        page += 1;
    }
    return deals;
}
