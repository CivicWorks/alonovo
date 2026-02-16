import { base } from '$app/paths';
import type { ClaimData, Company, User, ValueDef } from './types';

function apiBase(): string {
    return `${base}/api`;
}

function siteBase(): string {
    return base;
}

export async function fetchCompanies(): Promise<Company[]> {
    const response = await fetch(`${apiBase()}/companies/`);
    if (!response.ok) {
        throw new Error('Failed to fetch companies');
    }
    const data = await response.json();
    return data.results || data;
}

export async function fetchCompany(ticker: string): Promise<Company> {
    const response = await fetch(`${apiBase()}/companies/${ticker}/`);
    if (!response.ok) {
        throw new Error('Failed to fetch company');
    }
    return response.json();
}

export async function fetchValues(): Promise<ValueDef[]> {
    const response = await fetch(`${apiBase()}/values/`);
    if (!response.ok) {
        throw new Error('Failed to fetch values');
    }
    const data = await response.json();
    return data.results || data;
}

export async function fetchCompanyClaims(ticker: string): Promise<ClaimData[]> {
    const response = await fetch(`${apiBase()}/companies/${ticker}/claims/`);
    if (!response.ok) {
        throw new Error('Failed to fetch claims');
    }
    return response.json();
}

export async function fetchSectors(): Promise<string[]> {
    const response = await fetch(`${apiBase()}/sectors/`);
    if (!response.ok) {
        throw new Error('Failed to fetch sectors');
    }
    return response.json();
}

export async function fetchCurrentUser(): Promise<User | null> {
    const response = await fetch(`${apiBase()}/me/`, {
        credentials: 'include',
    });
    if (!response.ok) return null;
    return response.json();
}

export function getLoginUrl(): string {
    return `${base}/accounts/google/login/`;
}

export function getLogoutUrl(): string {
    return `${base}/accounts/logout/`;
}
