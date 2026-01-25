import "./style.css";

// --------------------------
// Company data with ids
// --------------------------
const companies = [
  {
    id: 0,
    name: "Costco",
    ticker: "COST",
    sector: "Retail",
    lobbying_spend: 1200000,
    grade: "A",
    reason: "Lowest lobbying spend among major retailers",
  },
  {
    id: 1,
    name: "McDonald's",
    ticker: "MCD",
    sector: "Restaurant",
    lobbying_spend: 1800000,
    grade: "A-",
    reason: "Low lobbying spend for company size",
  },
  {
    id: 2,
    name: "Starbucks",
    ticker: "SBUX",
    sector: "Restaurant",
    lobbying_spend: 2400000,
    grade: "B+",
    reason: "Moderate lobbying spend",
  },
  {
    id: 3,
    name: "Target",
    ticker: "TGT",
    sector: "Retail",
    lobbying_spend: 2800000,
    grade: "B+",
    reason: "Below average for major retailers",
  },
  {
    id: 4,
    name: "Home Depot",
    ticker: "HD",
    sector: "Retail",
    lobbying_spend: 3100000,
    grade: "B",
    reason: "Moderate lobbying spend",
  },
  {
    id: 5,
    name: "Bank of America",
    ticker: "BAC",
    sector: "Banking",
    lobbying_spend: 3200000,
    grade: "B",
    reason: "Lower than peer JPMorgan",
  },
  {
    id: 6,
    name: "JPMorgan Chase",
    ticker: "JPM",
    sector: "Banking",
    lobbying_spend: 3600000,
    grade: "B",
    reason: "Average for major banks",
  },
  {
    id: 7,
    name: "Disney",
    ticker: "DIS",
    sector: "Entertainment",
    lobbying_spend: 4200000,
    grade: "B-",
    reason: "Above average lobbying",
  },
  {
    id: 8,
    name: "Microsoft",
    ticker: "MSFT",
    sector: "Technology",
    lobbying_spend: 5140000,
    grade: "C+",
    reason: "High lobbying for tech sector",
  },
  {
    id: 9,
    name: "AT&T",
    ticker: "T",
    sector: "Telecom",
    lobbying_spend: 6000000,
    grade: "C",
    reason: "Significant telecom lobbying",
  },
  {
    id: 10,
    name: "Walmart",
    ticker: "WMT",
    sector: "Retail",
    lobbying_spend: 7240000,
    grade: "C",
    reason: "Highest among major retailers",
  },
  {
    id: 11,
    name: "Chevron",
    ticker: "CVX",
    sector: "Oil & Gas",
    lobbying_spend: 7500000,
    grade: "C-",
    reason: "High oil & gas lobbying",
  },
  {
    id: 12,
    name: "ExxonMobil",
    ticker: "XOM",
    sector: "Oil & Gas",
    lobbying_spend: 8700000,
    grade: "C-",
    reason: "Significant fossil fuel lobbying",
  },
  {
    id: 13,
    name: "Apple",
    ticker: "AAPL",
    sector: "Technology",
    lobbying_spend: 9500000,
    grade: "D+",
    reason: "High tech lobbying spend",
  },
  {
    id: 14,
    name: "Comcast",
    ticker: "CMCSA",
    sector: "Telecom",
    lobbying_spend: 10520000,
    grade: "D",
    reason: "Very high telecom/media lobbying",
  },
  {
    id: 15,
    name: "General Motors",
    ticker: "GM",
    sector: "Automotive",
    lobbying_spend: 10540000,
    grade: "D",
    reason: "Highest among automakers",
  },
  {
    id: 16,
    name: "Alphabet (Google)",
    ticker: "GOOGL",
    sector: "Technology",
    lobbying_spend: 11060000,
    grade: "D",
    reason: "Significant tech lobbying",
  },
  {
    id: 17,
    name: "Verizon",
    ticker: "VZ",
    sector: "Telecom",
    lobbying_spend: 11380000,
    grade: "D-",
    reason: "Highest telecom lobbying",
  },
  {
    id: 18,
    name: "Amazon",
    ticker: "AMZN",
    sector: "Retail/Tech",
    lobbying_spend: 14200000,
    grade: "F",
    reason: "Second highest overall lobbying",
  },
  {
    id: 19,
    name: "Meta (Facebook)",
    ticker: "META",
    sector: "Technology",
    lobbying_spend: 18850000,
    grade: "F",
    reason: "Highest lobbying among consumer companies",
  },
];

// --------------------------
// Helper functions
// --------------------------
function formatMoney(amount) {
  if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
  return `$${(amount / 1000).toFixed(0)}K`;
}

function getGradeClass(grade) {
  return `grade-${grade.charAt(0)}`;
}

function getSectors() {
  return [...new Set(companies.map((c) => c.sector))].sort();
}

function getStats(filtered) {
  const grades = filtered.map((c) => c.grade.charAt(0));
  const aCount = grades.filter((g) => g === "A").length;
  const fCount = grades.filter((g) => g === "F").length;
  const totalSpend = filtered.reduce((sum, c) => sum + c.lobbying_spend, 0);
  return { total: filtered.length, aCount, fCount, totalSpend };
}

function filterCompanies(search, sector, grade) {
  return companies.filter((c) => {
    const matchSearch =
      !search ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.ticker.toLowerCase().includes(search.toLowerCase());
    const matchSector = !sector || c.sector === sector;
    const matchGrade = !grade || c.grade.startsWith(grade);
    return matchSearch && matchSector && matchGrade;
  });
}

// --------------------------
// Render company card
// --------------------------
function renderCard(company) {
  return `
    <div class="company-card" data-id="${company.id}">
      <div class="card-header">
        <div>
          <h3 class="company-name">${company.name}</h3>
          <span class="company-ticker">${company.ticker}</span>
        </div>
        <div class="grade-badge ${getGradeClass(company.grade)}">${
    company.grade
  }</div>
      </div>
      <div class="card-body">
        <div class="sector">${company.sector}</div>
        <div class="spend">Lobbying: <strong>${formatMoney(
          company.lobbying_spend
        )}</strong> (2024)</div>
        <div class="grade-reason">${company.reason}</div>
      </div>
    </div>
  `;
}

// --------------------------
// Show company detail
// --------------------------
function showCompanyDetail(id) {
  const company = companies.find((c) => c.id === id);
  if (!company) return;

  const container = document.querySelector("#app");
  container.innerHTML = `
    <button id="back-btn">← Back</button>
    <div class="company-detail">
      <h2>${company.name} (${company.ticker})</h2>
      <p><strong>Sector:</strong> ${company.sector}</p>
      <p><strong>Lobbying spend (2024):</strong> ${formatMoney(
        company.lobbying_spend
      )}</p>
      <p><strong>Grade:</strong> ${company.grade}</p>
      <p><strong>Reason:</strong> ${company.reason}</p>
      <section style="margin-top:1rem;">
        <h3>How the grade is calculated</h3>
        <p>The grade is based solely on lobbying activities. Lower spending = better grade.</p>
        <ul>
          <li>Total lobbying expenditures</li>
          <li>Frequency and type of lobbying</li>
          <li>Organizations involved</li>
        </ul>
      </section>
    </div>
  `;

  document
    .querySelector("#back-btn")
    .addEventListener("click", () => render(companies));
}

// --------------------------
// Attach click listeners to cards
// --------------------------
function attachCardListeners() {
  const cards = document.querySelectorAll(".company-card");
  cards.forEach((card) => {
    const id = parseInt(card.dataset.id);
    card.addEventListener("click", () => showCompanyDetail(id));
  });
}

// --------------------------
// Render main app
// --------------------------
function render(filtered) {
  const stats = getStats(filtered);

  document.querySelector("#app").innerHTML = `
    <header>
      <h1>Alonovo</h1>
      <p class="tagline">Know before you buy. Know before you invest.</p>
      <p class="tagline">
        Grades powered by
        <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
      </p>
    </header>

    <main>
      <section class="intro">
        <h2>Corporate Lobbying Grades</h2>
        <p>How much do these companies spend to influence government policy?<br>
        <em>Lower spending = Better grade</em></p>
      </section>

      <div class="stats-bar">
        <div class="stat"><div class="stat-value">${
          stats.total
        }</div><div class="stat-label">Companies</div></div>
        <div class="stat"><div class="stat-value">${
          stats.aCount
        }</div><div class="stat-label">A Grades</div></div>
        <div class="stat"><div class="stat-value">${
          stats.fCount
        }</div><div class="stat-label">F Grades</div></div>
        <div class="stat"><div class="stat-value">${formatMoney(
          stats.totalSpend
        )}</div><div class="stat-label">Total Lobbying</div></div>
      </div>

      <div class="filters">
        <input type="text" id="search" placeholder="Search companies..." />
        <select id="sector-filter">
          <option value="">All Sectors</option>
          ${getSectors()
            .map((s) => `<option value="${s}">${s}</option>`)
            .join("")}
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
        ${filtered.map(renderCard).join("")}
      </div>
    </main>

    <footer>
      <p>Data sources: <a href="https://www.opensecrets.org" target="_blank">OpenSecrets</a>,
      <a href="https://www.statista.com" target="_blank">Statista</a> (2024)</p>
      <p><strong>Alonovo</strong> - Guiding capital toward ethical companies</p>
    </footer>
  `;

  // Attach listeners
  document.querySelector("#search").addEventListener("input", handleFilter);
  document
    .querySelector("#sector-filter")
    .addEventListener("change", handleFilter);
  document
    .querySelector("#grade-filter")
    .addEventListener("change", handleFilter);
  attachCardListeners();
}

// --------------------------
// Handle filters
// --------------------------
function handleFilter() {
  const search = document.querySelector("#search").value;
  const sector = document.querySelector("#sector-filter").value;
  const grade = document.querySelector("#grade-filter").value;
  const filtered = filterCompanies(search, sector, grade);

  const stats = getStats(filtered);

  document.querySelector(".stats-bar").innerHTML = `
    <div class="stat"><div class="stat-value">${
      stats.total
    }</div><div class="stat-label">Companies</div></div>
    <div class="stat"><div class="stat-value">${
      stats.aCount
    }</div><div class="stat-label">A Grades</div></div>
    <div class="stat"><div class="stat-value">${
      stats.fCount
    }</div><div class="stat-label">F Grades</div></div>
    <div class="stat"><div class="stat-value">${formatMoney(
      stats.totalSpend
    )}</div><div class="stat-label">Total Lobbying</div></div>
  `;

  document.querySelector(".company-grid").innerHTML = filtered
    .map(renderCard)
    .join("");
  attachCardListeners();
}

// --------------------------
// Initial render
// --------------------------
render(companies);
