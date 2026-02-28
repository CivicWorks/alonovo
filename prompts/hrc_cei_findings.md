# Corporate Equality Index (CEI) 2025 — Data Source & Scoring Overview

## TL;DR : There is a scraping source but we should contact them first - <mailto:cei@hrc.org> and we have to standardize the data.

## 1. Source References

- **Primary report:** Corporate Equality Index 2025 — “Rating Workplaces on Lesbian, Gay, Bisexual, Transgender and Queer Equality” (Human Rights Campaign Foundation, January 2025).
  - URL: <https://reports.hrc.org/corporate-equality-index-2025>
- **Overall employer ratings (PDF, Appendix A):**
  - PDF URL: <https://hrc-prod-requests.s3-us-west-2.amazonaws.com/Report-Design-Graphics/CEI-images/CEI-2024/CEI-2025-Appendix-A-Company-7.pdf>
- **Contact for additional data/info:**
  - Email: <mailto:cei@hrc.org>
- **Per-report note on employer-level scores:**
  - “Individual company scores based on the CEI criteria can be found online at www.hrc.org/cei/search.” (public search endpoint currently not working/accessible).

---

## 2. What the CEI 2025 Data Covers

- **Scope and purpose:**
  - The CEI is a benchmarking tool for U.S. businesses on LGBTQ+ workplace inclusion, focused on non‑discrimination protections, equitable benefits, inclusive culture, and corporate social responsibility.
- **Target organizations:**
  - Mid‑ to large‑sized businesses (generally 500+ full‑time employees), including Fortune 500 companies, AmLaw 200 law firms, and other major public and private employers.
- **Participation and coverage (2025 cycle):**
  - 1,449 companies officially rated in the 2025 CEI.
  - 765 businesses earned 100 points and the “Equality 100 Award: Leader in LGBTQ+ Workplace Inclusion.”
  - 72 new businesses participated in this edition, drawn from over 35 industries.
- **Geographic focus:**
  - Primary focus is on U.S. operations, with explicit consideration of global operations for nondiscrimination and benefits in companies that operate internationally.

---

## 3. Data Availability & Format

- **Public report format:**
  - The main CEI 2025 report is provided as a web report with narrative text, aggregate statistics, and high‑level tables/visuals.
  - Appendix A (employer ratings) is provided as a PDF listing individual companies and their scores; this is a human‑readable document, not a structured data file.
- **Per‑employer score details:**
  - The report states that individual company scores are available via a web search interface at `https://www.hrc.org/cei/search`, but that URL is currently non‑functional or inaccessible, and no public API is documented on the report site.
  - They might have migrated that interface to - `https://www.hrc.org/resources/employers/search`, which does work, so we could scrape from it. e.g. `https://www.hrc.org/resources/employers/search?q=costco`.
- **Machine‑readable/API access:**
  - No JSON/CSV export, schema description, or REST/GraphQL API is documented in the report or linked pages.
  - The practical, currently available machine‑readable route is manual extraction or scraping from the Appendix A PDF or any future CSV/HRC‑provided dataset.
- **Licensing / re‑use:**
  - The report does not state an explicit open‑data license in the visible sections; usage for commercial or bulk redistribution should be confirmed directly with HRC (via <mailto:cei@hrc.org>).

---

## 4. Rating System & Scoring Criteria (2025)

### 4.1 Overview

The CEI 2025 rating system is designed for mid‑ to large‑sized employers (generally 500+ FTEs) and is organized into four major criteria categories plus a responsible citizenship adjustment.

- Criteria 1 — Workforce Protections (5 points)
- Criteria 2 — Inclusive Benefits (50 points)
- Criteria 3 — Supporting an Inclusive Culture & Corporate Social Responsibility (25 points)  
- Criteria 4 — Corporate Social Responsibility (20 points)
- Criteria 5 — Responsible Citizenship (up to −25 points; deduction only)

Maximum CEI 2025 score is **100 points** before any Responsible Citizenship deductions.

---

### 4.2 Criteria 1 — Workforce Protections (5 points)

- **Points:** 5
- **Requirement:**
  - Employment non‑discrimination policy includes “sexual orientation” and “gender identity or expression” (or “gender identity”) across all operations.
- **Global operations:**
  - For companies with non‑U.S. operations, the policy must extend globally to the entire workforce.

---

### 4.3 Criteria 2 — Inclusive Benefits (50 points)

To secure full credit, each rated benefit must be available to all benefits‑eligible U.S. employees; where multiple plans exist, at least one inclusive plan must be available.

- **Total points:** 50
- **Sub‑components:**

1. Equivalency in same‑ and different‑sex spousal medical and soft benefits (10 points).
2. Equivalency in same‑ and different‑sex domestic partner medical and soft benefits (10 points).
3. Equal health coverage for transgender individuals without exclusion for medically necessary care (25 points), including:
   - Insurance contract explicitly affirms coverage, with no blanket exclusions for transition‑related care.
   - Policy documentation aligned with WPATH Standards of Care.
   - Plan documentation readily available, clearly communicating inclusive options to employees and dependents.
   - Other benefits available for other medical conditions are also available for transgender individuals, including short‑term medical leave, mental health benefits, pharmaceutical coverage, coverage for medical visits or lab services, and reconstructive surgical procedures related to transition.
4. LGBTQ+ Benefits Guide (5 points), where the employer provides an LGBTQ+ inclusive benefits guide for employees.

---

### 4.4 Criteria 3 — Supporting an Inclusive Culture & Corporate Social Responsibility (25 points)

- **Total points:** 25

**a. LGBTQ+ Internal Training and Accountability (5 points)**
Businesses must show a sustained firm‑wide commitment, including at least four of:

- New‑hire training clearly stating that the nondiscrimination policy includes gender identity and sexual orientation, with definitions or scenarios.
- Supervisor training covering gender identity and sexual orientation as explicit topics.
- Integration of gender identity and sexual orientation into professional development or leadership training that includes diversity and cultural competency.
- Senior management or executive performance measures include LGBTQ+ diversity metrics.
- Integration of intersectionality in professional development or training (required for credit).

**b. LGBTQ+ Data Collection (5 points)**
At least one of:

- Anonymous engagement or climate surveys (annual or biennial) allowing employees to identify as LGBTQ+.
- HR data collection including optional questions on sexual orientation and gender identity alongside other demographics.
- Board or governing body demographic data collection including sexual orientation, gender identity, or LGBTQ+ self‑identification.

**c. Transgender Inclusion Best Practices (5 points)**

- Gender transition guidelines with supportive restroom, dress code, and documentation guidance.
- Plus at least one of: trans‑inclusive restroom/facilities policy, gender‑neutral dress code, or policies allowing optional sharing of gender pronouns.

**d. Employee Group or Diversity Council (10 points)**

- Either an LGBTQ+ Employee Resource Group or an LGBTQ+ Diversity Council.

---

### 4.5 Criteria 4 — Corporate Social Responsibility (20 points)

- **Total points:** 20

**a. LGBTQ+ Outreach / Engagement to the Broader Community (15 points)**

Ongoing LGBTQ+‑specific engagement, including at least five of:

- LGBTQ+ recruitment efforts with demonstrated reach.
- Supplier diversity program including certified LGBTQ+ suppliers.
- Marketing or advertising to LGBTQ+ consumers (e.g., LGBTQ+ content, media, sponsorships).
- Philanthropic support of LGBTQ+ organizations or events.
- Public support for LGBTQ+ equality via legislation or initiatives.
- LGBTQ+ inclusive products and services.

**b. LGBTQ+ Corporate Social Responsibility (5 points)**

- Contractor or supplier non‑discrimination standards.
- Philanthropic giving guidelines that include LGBTQ+ considerations.

---

### 4.6 Criteria 5 — Responsible Citizenship (up to −25 points)

- **Adjustment:** Up to 25 points may be deducted from an employer’s score for large‑scale official or public anti‑LGBTQ+ incidents or “blemishes” on their recent record.
- **Scope:**
  - Based on information HRC becomes aware of regarding actions harmful to LGBTQ+ equality and inclusion, as further described in the “Responsible Citizenship in the Corporate Equality Index” section referenced by the report.

---

## 5. Data Source Research Summary

1. **What the data source covers**
   - CEI 2025 rates 1,449 mid‑ to large‑sized businesses on LGBTQ+ workplace inclusion using a 0–100 scoring system built on four criteria (workforce protections, inclusive benefits, inclusive culture, CSR) plus a responsible citizenship penalty.
   - Companies include Fortune 500 firms, AmLaw 200 law firms, and other large employers, together representing over 22 million workers in the United States.

2. **How many companies and what information exists**
   - 1,449 rated companies, including 765 that achieved 100 points and the “Equality 100 Award” designation.
   - Aggregate statistics by criterion (e.g., percentage of companies with protections or inclusive benefits) are available in the report, while employer‑level scores are listed in Appendix A and referenced as searchable via a web interface.

3. **Format of the data**
   - Public outputs are the HTML web report plus a PDF appendix for employer ratings.
   - No officially documented JSON/CSV or public API is exposed; employer‑level data is human‑oriented and would require manual or scripted extraction from PDFs or any internal/undocumented endpoints.

4. **Availability and access constraints**
   - The report references a public search endpoint at `www.hrc.org/cei/search` for individual company scores, but this URL is not currently accessible, and the report itself does not document any API.
   - For programmatic or bulk access, practical options are:
     - Contacting HRC at <mailto:cei@hrc.org> to request bulk data or an official data feed.
     - Extracting data from the Appendix A PDF, subject to legal and terms‑of‑use constraints.

---

## 6. Sample JSON Representation for Detailed Ratings

Below is an example schema for representing one employer’s ratings in JSON, aligned with the CEI structure and using the “workforce protections” example:

```json
{
  "ticker": "EXAMPLE-TICKER",  # couldn't find ticker information though
  "company_name": "EXAMPLE-COMPANY",
  "cei_year": 2025,
  "overall_score": 100,
  "criteria": [
    {
      "id": 1,
      "title": "Workforce Protections",
      "points": "5/5",
      "sub_criteria": [
        {
          "description": "Employment non-discrimination policy includes sexual orientation and gender identity for all operations",
          "satisfied": true
        }
      ]
    },
    {
      "id": 2,
      "title": "Inclusive Benefits",
      "points": "50/50",
      "sub_criteria": [
        {
          "description": "Equivalency in same- and different-sex spousal medical and soft benefits",
          "satisfied": true
        },
        {
          "description": "Equivalency in same- and different-sex domestic partner medical and soft benefits",
          "satisfied": true
        },
        {
          "description": "Equal health coverage for transgender individuals without exclusion for medically necessary care",
          "satisfied": true
        },
        {
          "description": "LGBTQ+ inclusive benefits guide provided to employees",
          "satisfied": true
        }
      ]
    }
  ]
}
