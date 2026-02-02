# KnowTheChain Benchmark Data — Data Source & Scoring Overview

## TL;DR : There is a usable scraping source, but we should treat it as curated data and contact them first — mailto:info@knowthechain.org / mailto:contact@business-humanrights.org — and we have to standardize and filter the data, especially to restrict companies to the U.S. where needed since the benchmark covers multiple countries.

## 1. Source References

- **Primary portal:** KnowTheChain benchmark data hub (Business & Human Rights Resource Centre).
  - URL: <https://www.business-humanrights.org/en/from-us/knowthechain/benchmark-data/>
- **General contact (Business & Human Rights Resource Centre):**
  - Email: <mailto:contact@business-humanrights.org>
- **KnowTheChain-specific contact:**
  - Email: <mailto:info@knowthechain.org>
- **Sample dataset used here:**  
  - File: `KTC-2025-ICT-benchmark-data.xlsx` (2025 ICT benchmark full dataset).

---

## 2. What KnowTheChain Covers

- **Purpose and focus:**
  - KnowTheChain is a resource for companies and investors to address forced labour in global supply chains, using benchmarks to incentivize better practices and expose gaps.
- **Benchmark sectors:**
  - Benchmarks are run across three high‑risk sectors: **Information & Communications Technology (ICT)**, **Apparel & Footwear**, and **Food & Beverage**.
- **Frequency and scope:**
  - Benchmarks are **biennial**, with each cycle assessing dozens of the largest global companies in each sector (e.g., 45 ICT companies in the 2025 benchmark).
  - Earlier cycles expanded from 60 companies in 2016 to over 100 in later years, and the 2025–26 methodology anticipates 145 companies across all three sectors.

### 2.1 Information & Communications Technology (ICT)

- The 2025 ICT benchmark covers **45 major ICT companies** (e.g., semiconductor, hardware, communications equipment) and provides total benchmark scores, theme scores, and indicator‑level scores per company.
- Research for the 2025 ICT benchmark draws on public company disclosures, additional information submitted by companies during an engagement window, and forced labour allegations from reputable third‑party sources.

### 2.2 Apparel & Footwear

- KnowTheChain runs a separate benchmark for global apparel and footwear brands, using the same overarching framework (forced labour risk in supply chains) but applied to apparel supply chains.
- Companies are assessed on public disclosure and additional information they provide, with results published as sector‑specific benchmark reports and downloadable datasets (after newsletter sign‑up).

### 2.3 Food & Beverage

- A third benchmark covers food and beverage companies, again focusing on forced labour risk and responsible supply chain practices in agricultural and food production chains.
- As with the other sectors, the benchmark scores companies on a common framework, allowing cross‑sector comparison on key themes such as recruitment, purchasing practices, and worker voice.

### 2.4 Access model and licensing / re‑use

- **Access model:**
  - Sector benchmark data (scores and detailed research) is downloadable as compressed PDFs and spreadsheets (e.g., XLSX) after completing a newsletter sign‑up form that requests **email, first name, and last name**; fields like organization and position are optional.
  - The sample ICT dataset explicitly describes itself as the “full dataset” for 45 ICT companies in the 2025 benchmark, including scoring and detailed research comments.
- **Licensing / re‑use:**
  - Neither the benchmark data landing page nor the public methodology pages clearly state an explicit open‑data license (e.g., CC‑BY) for bulk reuse; they present the data as a research and engagement resource.
  - Given the lack of an explicit license, it is prudent to seek clarification or permission via <mailto:contact@business-humanrights.org> or <mailto:info@knowthechain.org>.

---

## 3. Data Availability & Format

- **Public web content:**
  - Each benchmark has public narrative pages summarizing core findings, average scores, and key thematic weaknesses (e.g., 2025 ICT findings).
  - A general KnowTheChain landing page explains the initiative and links to benchmarks, methodology, and resources.
- **Downloadable benchmark datasets:**
  - For each sector and cycle, KnowTheChain provides downloadable datasets that include:
    - Total benchmark score per company
    - Theme‑level scores
    - Indicator and indicator‑element scores
    - Research comments and citations
    - Non‑scored research metadata (e.g., legal reporting obligations, high‑risk sourcing disclosures) (ticker appears here)
  - These files are offered in **XLSX** format and as **compressed PDFs** that present scores and company findings in a report‑style layout.
- **Structure of the XLSX (ICT example):**
  - The 2025 ICT dataset describes itself as containing three main components:
    1. **Scoring** — total benchmark score, theme scores, and indicator scores per company.
    2. **Detailed scoring research** — indicator‑element scores plus research comments and source links.
    3. **Non‑scored research** — contextual data on legislation, high‑risk locations, etc.
  - Company‑level columns include identifiers (ID, name, year of inclusion, country, region, sub‑industry, market cap) and scores for 12 indicators and 7 aggregate themes such as Commitment & Governance, Purchasing Practices, Recruitment, Enabling Workers’ Rights, Monitoring, and Remedy.
- **Update frequency and workflow:**
  - Benchmarks are **biennial**, and research windows typically span several months, including a company engagement phase where companies can review and supplement findings; the full dataset is then published for that cycle.
  - A practical workflow is to **download the XLSX/PDF files manually** for each new cycle (roughly every two years) and then parse, normalize, and load them into your own system for analysis or pipelines.

### 3.1 API / scraping considerations

- There is **no documented public API** for programmatic access to the benchmark data on the KnowTheChain or Business & Human Rights Resource Centre sites, nor any reference to JSON/CSV feeds or an open developer interface.
- Download links are standard HTTP endpoints behind a simple newsletter sign‑up form; nothing indicates a formal restriction on automated download beyond normal terms of use.
- Given the small update frequency (biennial) and the richness of the XLSX file, the current approach — **manual download then local parsing and processing** — is advised.

---

## 4. Rating System & Scoring Criteria (Benchmark Methodology)

### 4.1 Overall framework

- KnowTheChain’s methodology framework assesses companies against **seven overarching themes**:
  1. Commitment & governance
  2. Traceability & risk assessment
  3. Purchasing practices
  4. Recruitment
  5. Worker voice / enabling workers’ rights
  6. Monitoring
  7. Remedy
- For the ICT 2025 dataset, this is operationalized as **12 indicators**, each broken into **indicator “elements”** with qualitative criteria, and aggregated into an overall score out of 100.

### 4.2 Themes and indicators (ICT 2025 example)

From the ICT dataset structure and the methodology framework, the indicators and themes can be summarized as follows (naming simplified but aligned with the file):

- **Theme: Commitment & governance**
  - Indicator 1: Supplier Code of Conduct & capacity building
  - Indicator 2: Management & accountability
- **Theme: Traceability & risk assessment**
  - Indicator 3: Traceability & supply chain transparency
  - Indicator 4: Risk assessment
  - Indicator 5: Data on supply chain risks
- **Theme: Purchasing practices**
  - Indicator 6: Purchasing practices
- **Theme: Recruitment**
  - Indicator 7: Recruitment fees & related costs (Employer Pays Principle)
  - Indicator 8: Responsible recruitment
- **Theme: Enabling workers’ rights (worker voice / freedom of association)**
  - Indicator 9: Freedom of association
  - Indicator 10: Grievance mechanism
- **Theme: Monitoring**
  - Indicator 11: Monitoring
- **Theme: Remedy**
  - Indicator 12: Remedy

Each indicator (e.g., “6. Purchasing Practices”) is broken into **elements** (6.1, 6.2, 6.3), each with a qualitative description that forms the scoring rubric (e.g., contracts embedding shared responsibility, adoption of responsible purchasing practices, and disclosure of quantitative data on purchasing impacts).

### 4.3 Scoring structure

- **Indicator elements:**
  - Each element (e.g., 1.1, 1.2, 6.1, 6.2, 6.3) has a detailed textual criterion describing what a company must disclose or do to receive credit, along with research comments and source citations per company.
- **Indicator scores:**
  - For each indicator, KnowTheChain assigns a numeric score derived from the underlying element scores; these are reported per company in the scoring sheet.
- **Theme scores:**
  - Indicators are grouped into themes; the dataset includes columns for theme‑level scores such as “Commitment & governance,” “Purchasing practices,” “Recruitment,” “Enabling workers’ rights,” “Monitoring,” and “Remedy.”
- **Total benchmark score:**
  - A “Total benchmark score 2025” column reports each company’s aggregated score out of 100, along with the rank within the benchmark (e.g., Samsung 61/100, HPE 53/100, Cisco 51/100 in the 2025 ICT benchmark).

### 4.4 Research process and evidence

- Research is conducted through **desktop review** of company public disclosures and additional disclosures submitted by companies over a dedicated review period, supplemented by **allegations of forced labour** from reputable third‑party sources.
- For each indicator element, the dataset contains:
  - A narrative research comment explaining whether and how the company meets the criterion.
  - Source references (URLs, reports, statements, etc.).
  - Element‑level scores that roll up to indicator and theme scores.

---

## 5. Data Source Research Summary

1. **What the data source covers**
   - KnowTheChain benchmarks evaluate large global companies in ICT, apparel & footwear, and food & beverage on their efforts to prevent forced labour in supply chains, using a structured methodology with themes, indicators, and qualitative criteria.
   - The 2025 ICT benchmark dataset includes 45 ICT companies and provides total scores, theme scores, indicator scores, and underlying research comments and sources for each indicator element.

2. **How many companies and what information exists**
   - Across cycles, KnowTheChain has assessed well over 100 companies per cycle across the three sectors, with the 2025–26 methodology targeting 145 companies in total.
   - For each company, the dataset includes: basic profile (ID, name, region, industry, market cap), 12 indicator scores, 7 theme scores, total benchmark score and rank, plus narrative evidence and external source references.

3. **Format of the data**
   - Core data is available as downloadable XLSX and compressed PDF files after a newsletter sign‑up gate; the XLSX file is machine‑readable and well‑structured for parsing.
   - The XLSX separates high‑level scoring from detailed research and non‑scored contextual information, making it suitable for ETL into our own database or analytics stack.

4. **Availability and access constraints**  
   - There is no documented open API or explicit open‑data license; access is mediated through a basic sign‑up form, and the data is framed as a research and engagement tool rather than open data.
   - Given the **biennial** update cycle and the availability of full XLSX datasets, a pragmatic approach is to manually download new releases when available and then parse and store them locally.

---

## 6. Sample JSON Representation for Detailed Benchmark Scores

Below is an example JSON structure to represent one company’s KnowTheChain ICT benchmark results in our own system, aligned with the 2025 ICT dataset and methodology.

```json
{
  "company_id": 759165,
  "company_name": "Samsung Electronics Co. Ltd.",
  "benchmark": "KnowTheChain",
  "sector": "ICT",
  "benchmark_year": 2025,
  "country": "South Korea",
  "region": "Asia",
  "subindustry": "Technology Hardware, Storage & Peripherals",
  "market_cap_usd_billion": 377.1,
  "overall_score": 61,
  "rank": 1,
  "themes": [
    {
      "name": "Commitment & governance",
      "score": 80
    },
    {
      "name": "Traceability & risk assessment",
      "score": 69
    },
    {
      "name": "Purchasing practices",
      "score": 34
    },
    {
      "name": "Recruitment",
      "score": 84
    },
    {
      "name": "Enabling workers' rights",
      "score": 40
    },
    {
      "name": "Monitoring",
      "score": 50
    },
    {
      "name": "Remedy",
      "score": 40
    }
  ],
  "indicators": [
    {
      "id": 1,
      "code": "1",
      "title": "Supplier Code of Conduct & Capacity Building",
      "theme": "Commitment & governance",
      "score": 75,
      "elements": [
        {
          "element_code": "1.1",
          "description": "Supplier code of conduct covers ILO core labour standards including forced labour and requires cascading to sub-suppliers",
          "score": 100,
          "evidence_summary": "Supplier code aligned with RBA Code of Conduct; requirements extend to next-tier suppliers.",
          "sources": [
            "https://www.amd.com/en/corporate/corporate-responsibility/amd-supplier-code-of-conduct.html"
          ]
        },
        {
          "element_code": "1.2",
          "description": "Capacity building to enable suppliers to implement and cascade forced labour standards",
          "score": 50,
          "evidence_summary": "Participation in forced labour prevention workshops; training for first-tier suppliers; limited disclosure on deeper tiers.",
          "sources": [
            "https://www.amd.com/content/dam/amd/en/documents/corporate/cr/corporate-responsibility-report.pdf"
          ]
        }
      ]
    },
    {
      "id": 6,
      "code": "6",
      "title": "Purchasing Practices",
      "theme": "Purchasing practices",
      "score": 34,
      "elements": [
        {
          "element_code": "6.1",
          "description": "Contracts embed shared responsibility for human rights due diligence with suppliers",
          "score": 75,
          "evidence_summary": "Standard contracts reference shared responsibility but limited operational detail.",
          "sources": []
        },
        {
          "element_code": "6.2",
          "description": "Adoption of responsible purchasing practices (planning, forecasting, fair pricing including labour costs)",
          "score": 0,
          "evidence_summary": "No clear disclosure of how purchasing practices are adjusted to protect labour rights.",
          "sources": []
        },
        {
          "element_code": "6.3",
          "description": "Quantitative data on purchasing practices and impacts (e.g., payment terms, order changes)",
          "score": 25,
          "evidence_summary": "Some quantitative disclosure (e.g., payment terms, order stability), but limited linkage to forced labour risk mitigation.",
          "sources": []
        }
      ]
    }
  ],
  "non_scored_research": {
    "legal_reporting_obligations": {
      "uk_modern_slavery_act": true,
      "california_transparency_in_supply_chains_act": true,
      "australia_modern_slavery_act": false
    },
    "high_risk_sourcing": [
      "Xinjiang region (China) allegations related to suppliers and raw materials"
    ]
  },
  "allegations": [
    {
      "summary": "Allegations of linkages to suppliers implicated in forced Uyghur labour in Xinjiang through minerals and components supply chains.",
      "sources": [
        "https://c4ads.org",
        "https://www.aspi.org.au/report/uyghurs-sale"
      ],
      "company_response_summary": "Company referenced industry initiatives and supplier standards; limited evidence of direct engagement with affected workers.",
      "score_impact": 0
    }
  ]
}
