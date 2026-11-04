// Search scoring shared by /shop and /blackfriday

export function tokens(text: string): string[] {
    return text.toLowerCase().replace(/_/g, ' ').split(/[^a-z0-9'&]+/).filter(Boolean);
}

// How well one typed word matches a list of words: whole word (or plural) 3, word start 1
export function wordScore(w: string, toks: string[]): number {
    const stem = w.replace(/e?s$/, '');
    let best = 0;
    for (const t of toks) {
        if (t === w || t === stem || t.replace(/e?s$/, '') === stem) return 3;
        if (t.startsWith(w)) best = 1;
    }
    return best;
}

// Every typed word must match; the name counts most, then brand, then the rest (company, category).
// `needle` is the whole query, lower-cased and trimmed; `words` is it split on spaces.
export function searchScore(words: string[], needle: string, name: string, brand: string, rest: string): number {
    const n = tokens(name), b = tokens(brand), r = tokens(rest);
    let total = 0;
    for (const w of words) {
        const s = Math.max(wordScore(w, n) * 3, wordScore(w, b) * 2, wordScore(w, r));
        if (!s) return 0;
        total += s;
    }
    if (name.toLowerCase() === needle || brand.toLowerCase() === needle) total += 20;
    // Among equal matches, a name with fewer extra words is the closer match
    return total + words.length / Math.max(n.length, 1);
}
