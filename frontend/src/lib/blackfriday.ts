// Black Friday page: bigger purchases and where people buy them. Hand-picked from the companies
// Alonovo grades (by ticker); edit this list to change the page.
export const BLACK_FRIDAY_SECTIONS = [
    { title: 'Phones, laptops and TVs', tickers: ['AAPL', '005930.KS', 'GOOGL', 'MSFT', 'DELL', 'HPQ', 'GRMN'] },
    { title: 'Clothes, shoes and fashion', tickers: ['NKE', 'ADS.DE', 'LULU', 'UAA', 'LEVI', 'GPS', 'RL', 'PVH', 'TPR', 'VFC'] },
    { title: 'Home and appliances', tickers: ['WHR', 'HD', 'LOW'] },
    { title: 'Beauty', tickers: ['EL', 'ULTA'] },
    { title: 'Toys and entertainment', tickers: ['HAS', 'DIS'] },
    { title: 'Cars', tickers: ['TSLA', 'F', 'GM'] },
    { title: 'Where to buy', tickers: ['AMZN', 'WMT', 'TGT', 'COST', 'BBY', 'TJX', 'ROST', 'DKS', 'ASO'] },
];

// Shopper-facing categories on the Black Friday page. `deals` are deal categories as the store
// lists them (Cause-Cart today); `sections` are titles from BLACK_FRIDAY_SECTIONS above.
export const BLACK_FRIDAY_CATEGORIES = [
    { name: 'Home', deals: ['Home Décor'], sections: ['Home and appliances'] },
    { name: 'Fashion', deals: ['Apparel', 'Jewelry', 'Accessories'], sections: ['Clothes, shoes and fashion'] },
    { name: 'Beauty', deals: ['Beauty'], sections: ['Beauty'] },
    { name: 'Electronics', deals: [], sections: ['Phones, laptops and TVs'] },
    { name: 'Food', deals: ['Grocery & Gourmet Food'], sections: [] },
];
