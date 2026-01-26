import { PUBLIC_API_URL } from '$env/static/public';
import type { Company } from './types';

export async function fetchCompanies(): Promise<Company[]> {
    const response = await fetch(`${PUBLIC_API_URL}/companies/`);
    if (!response.ok) {
        throw new Error('Failed to fetch companies');
    }
    const data = await response.json();
    return data.results || data;
}

export async function fetchCompany(ticker: string): Promise<Company> {
    const response = await fetch(`${PUBLIC_API_URL}/companies/${ticker}/`);
    if (!response.ok) {
        throw new Error('Failed to fetch company');
    }
    return response.json();
}
