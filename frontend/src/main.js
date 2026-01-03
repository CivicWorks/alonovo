import './style.css'

// Company data with lobbying grades (2024)
const companies = [
  { name: "Costco", ticker: "COST", sector: "Retail", lobbying_spend: 1200000, grade: "A", reason: "Lowest lobbying spend among major retailers" },
  { name: "McDonald's", ticker: "MCD", sector: "Restaurant", lobbying_spend: 1800000, grade: "A-", reason: "Low lobbying spend for company size" },
  { name: "Starbucks", ticker: "SBUX", sector: "Restaurant", lobbying_spend: 2400000, grade: "B+", reason: "Moderate lobbying spend" },
  { name: "Target", ticker: "TGT", sector: "Retail", lobbying_spend: 2800000, grade: "B+", reason: "Below average for major retailers" },
  { name: "Home Depot", ticker: "HD", sector: "Retail", lobbying_spend: 3100000, grade: "B", reason: "Moderate lobbying spend" },
  { name: "Bank of America", ticker: "BAC", sector: "Banking", lobbying_spend: 3200000, grade: "B", reason: "Lower than peer JPMorgan" },
  { name: "JPMorgan Chase", ticker: "JPM", sector: "Banking", lobbying_spend: 3600000, grade: "B", reason: "Average for major banks" },
  { name: "Disney", ticker: "DIS", sector: "Entertainment", lobbying_spend: 4200000, grade: "B-", reason: "Above average lobbying" },
  { name: "Microsoft", ticker: "MSFT", sector: "Technology", lobbying_spend: 5140000, grade: "C+", reason: "High lobbying for tech sector" },
  { name: "AT&T", ticker: "T", sector: "Telecom", lobbying_spend: 6000000, grade: "C", reason: "Significant telecom lobbying" },
  { name: "Walmart", ticker: "WMT", sector: "Retail", lobbying_spend: 7240000, grade: "C", reason: "Highest among major retailers" },
  { name: "Chevron", ticker: "CVX", sector: "Oil & Gas", lobbying_spend: 7500000, grade: "C-", reason: "High oil & gas lobbying" },
  { name: "ExxonMobil", ticker: "XOM", sector: "Oil & Gas", lobbying_spend: 8700000, grade: "C-", reason: "Significant fossil fuel lobbying" },
  { name: "Apple", ticker: "AAPL", sector: "Technology", lobbying_spend: 9500000, grade: "D+", reason: "High tech lobbying spend" },
  { name: "Comcast", ticker: "CMCSA", sector: "Telecom", lobbying_spend: 10520000, grade: "D", reason: "Very high telecom/media lobbying" },
  { name: "General Motors", ticker: "GM", sector: "Automotive", lobbying_spend: 10540000, grade: "D", reason: "Highest among automakers" },
  { name: "Alphabet (Google)", ticker: "GOOGL", sector: "Technology", lobbying_spend: 11060000, grade: "D", reason: "Significant tech lobbying" },
  { name: "Verizon", ticker: "VZ", sector: "Telecom", lobbying_spend: 11380000, grade: "D-", reason: "Highest telecom lobbying" },
  { name: "Amazon", ticker: "AMZN", sector: "Retail/Tech", lobbying_spend: 14200000, grade: "F", reason: "Second highest overall lobbying" },
  { name: "Meta (Facebook)", ticker: "META", sector: "Technology", lobbying_spend: 18850000, grade: "F", reason: "Highest lobbying among consumer companies" },
];

// Format currency
function formatMoney(amount) {
  if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(1)}M`;
  }
  return `$${(amount / 1000).toFixed(0)}K`;
}

// Get grade class
function getGradeClass(grade) {
  const letter = grade.charAt(0);
  return `grade-${letter}`;
}

// Get unique sectors
function getSectors() {
  return [...new Set(companies.map(c => c.sector))].sort();
}

// Calculate stats
function getStats(filtered) {
  const grades = filtered.map(c => c.grade.charAt(0));
  const aCount = grades.filter(g => g === 'A').length;
  const fCount = grades.filter(g => g === 'F').length;
  const totalSpend = filtered.reduce((sum, c) => sum + c.lobbying_spend, 0);
  return { total: filtered.length, aCount, fCount, totalSpend };
}

// Render company card
function renderCard(company) {
  return `
    <div class="company-card">
      <div class="card-header">
        <div>
          <h3 class="company-name">${company.name}</h3>
          <span class="company-ticker">${company.ticker}</span>
        </div>
        <div class="grade-badge ${getGradeClass(company.grade)}">${company.grade}</div>
      </div>
      <div class="card-body">
        <div class="sector">${company.sector}</div>
        <div class="spend">Lobbying: <strong>${formatMoney(company.lobbying_spend)}</strong> (2024)</div>
        <div class="grade-reason">${company.reason}</div>
      </div>
    </div>
  `;
}

// Filter companies
function filterCompanies(search, sector, grade) {
  return companies.filter(c => {
    const matchSearch = !search ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.ticker.toLowerCase().includes(search.toLowerCase());
    const matchSector = !sector || c.sector === sector;
    const matchGrade = !grade || c.grade.startsWith(grade);
    return matchSearch && matchSector && matchGrade;
  });
}

// Render app
function render(filtered) {
  const stats = getStats(filtered);

  document.querySelector('#app').innerHTML = `
    <header>
      <h1>Alonovo</h1>
      <p class="tagline">Know before you buy. Know before you invest.</p>
    </header>

    <main>
      <section class="intro">
        <h2>Corporate Lobbying Grades</h2>
        <p>How much do these companies spend to influence government policy?<br>
        <em>Lower spending = Better grade</em></p>
      </section>

      <div class="stats-bar">
        <div class="stat">
          <div class="stat-value">${stats.total}</div>
          <div class="stat-label">Companies</div>
        </div>
        <div class="stat">
          <div class="stat-value">${stats.aCount}</div>
          <div class="stat-label">A Grades</div>
        </div>
        <div class="stat">
          <div class="stat-value">${stats.fCount}</div>
          <div class="stat-label">F Grades</div>
        </div>
        <div class="stat">
          <div class="stat-value">${formatMoney(stats.totalSpend)}</div>
          <div class="stat-label">Total Lobbying</div>
        </div>
      </div>

      <div class="filters">
        <input type="text" id="search" placeholder="Search companies..." />
        <select id="sector-filter">
          <option value="">All Sectors</option>
          ${getSectors().map(s => `<option value="${s}">${s}</option>`).join('')}
        </select>
        <select id="grade-filter">
          <option value="">All Grades</option>
          <option value="A">A grades</option>
          <option value="B">B grades</option>
          <option value="C">C grades</option>
          <option value="D">D grades</option>
          <option value="F">F grade</option>
        </select>
      </div>

      <div class="company-grid">
        ${filtered.map(renderCard).join('')}
      </div>
    </main>

    <footer>
      <p>Data sources: <a href="https://www.opensecrets.org" target="_blank">OpenSecrets</a>,
      <a href="https://www.statista.com" target="_blank">Statista</a> (2024)</p>
      <p><strong>Alonovo</strong> - Guiding capital toward ethical companies</p>
    </footer>
  `;

  // Attach event listeners
  document.querySelector('#search').addEventListener('input', handleFilter);
  document.querySelector('#sector-filter').addEventListener('change', handleFilter);
  document.querySelector('#grade-filter').addEventListener('change', handleFilter);
}

// Handle filter changes
function handleFilter() {
  const search = document.querySelector('#search').value;
  const sector = document.querySelector('#sector-filter').value;
  const grade = document.querySelector('#grade-filter').value;
  const filtered = filterCompanies(search, sector, grade);

  // Only update grid and stats, preserve filter values
  const stats = getStats(filtered);

  document.querySelector('.stats-bar').innerHTML = `
    <div class="stat">
      <div class="stat-value">${stats.total}</div>
      <div class="stat-label">Companies</div>
    </div>
    <div class="stat">
      <div class="stat-value">${stats.aCount}</div>
      <div class="stat-label">A Grades</div>
    </div>
    <div class="stat">
      <div class="stat-value">${stats.fCount}</div>
      <div class="stat-label">F Grades</div>
    </div>
    <div class="stat">
      <div class="stat-value">${formatMoney(stats.totalSpend)}</div>
      <div class="stat-label">Total Lobbying</div>
    </div>
  `;

  document.querySelector('.company-grid').innerHTML = filtered.map(renderCard).join('');
}

// Initial render
render(companies);
