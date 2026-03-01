export interface Category {
    slug: string;
    name: string;
    valueSlugs: string[];
    isDisqualifying?: boolean;
}

export const CATEGORIES: Category[] = [
    { slug: 'political_lobbying', name: 'Political Lobbying', valueSlugs: ['corporate_lobbying'] },
    { slug: 'executive_pay', name: 'Executive Pay Ratios', valueSlugs: ['ethics_of_executives'] },
    { slug: 'carbon_footprint', name: 'Carbon Footprint', valueSlugs: ['esg_score'] },
    { slug: 'ice_collaboration', name: 'ICE Collaboration', valueSlugs: ['ice_contracts', 'ice_detention', 'ice_collaborator'], isDisqualifying: true },
    { slug: 'animal_welfare', name: 'Animal Welfare', valueSlugs: ['farm_animal_welfare', 'cage_free_eggs', 'cruelty_free'] },
    { slug: 'stood_up', name: 'Stood Up', valueSlugs: ['stood_up'] },
    { slug: 'fair_labor', name: 'Fair Labor/Anti-Union', valueSlugs: [] },
    { slug: 'dei_policies', name: 'DEI Policies', valueSlugs: [] },
    { slug: 'supply_chain', name: 'Supply Chain Standards', valueSlugs: [] },
];
