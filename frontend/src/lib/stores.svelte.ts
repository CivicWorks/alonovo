import { fetchCurrentUser, fetchWeights } from './api';
import type { User } from './types';

// --- User state ---
let _user: User | null = $state(null);
let _userLoaded = $state(false);

export function getUser(): User | null { return _user; }
export function isUserLoaded(): boolean { return _userLoaded; }

export async function loadUser(): Promise<User | null> {
    if (_userLoaded) return _user;
    _user = await fetchCurrentUser();
    _userLoaded = true;
    return _user;
}

// --- Personalization toggle ---
let _personalized = $state(true);

export function isPersonalized(): boolean {
    return _user !== null && _personalized;
}

export function setPersonalized(val: boolean): void {
    _personalized = val;
}

export function getPersonalizedRaw(): boolean {
    return _personalized;
}

// --- User weights ---
let _weights: Record<string, number> = $state({});
let _weightsLoaded = $state(false);

export function getWeights(): Record<string, number> { return _weights; }
export function areWeightsLoaded(): boolean { return _weightsLoaded; }

export async function loadWeights(): Promise<Record<string, number>> {
    if (_weightsLoaded) return _weights;
    if (!_user) return {};
    try {
        const data = await fetchWeights();
        for (const w of data) {
            _weights[w.value_slug] = w.weight;
        }
    } catch (e) {
        console.error('Failed to load weights', e);
    }
    _weightsLoaded = true;
    return _weights;
}
