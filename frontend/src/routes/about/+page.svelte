<script lang="ts">
    import { base } from '$app/paths';
</script>

<div class="about-page">
    <a href="{base}/" class="back-btn">&larr; Back to companies</a>

    <h1>About Alonovo</h1>

    <section>
        <p>
            Alonovo helps consumers and investors make informed, ethical choices.
            We aggregate data from trusted institutional sources to grade companies
            on the issues that matter — from corporate lobbying and farm animal welfare
            to ICE contracts and ESG performance.
        </p>
        <p>
            <strong>Know before you buy. Know before you invest.</strong>
        </p>
    </section>

    <section>
        <h2>A Joint Project</h2>
        <p>
            Alonovo is a collaboration between
            <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
            and
            <a href="https://civ.works" target="_blank" rel="noreferrer">Civic Works</a>.
        </p>

        <h3>Civic Works</h3>
        <p>
            <a href="https://civ.works" target="_blank" rel="noreferrer">Civic Works</a>
            is a 501(c)(3) non-profit building an ad-free civic social network
            for civic action and education. Because civ.works is the product, not you.
            Think Netflix for Democracy. Led by Executive Director George A. Polisner
            with 30+ years of technology and development experience, and CTO Golda Velez,
            Civic Works prioritizes democratic participation and civic engagement
            over data monetization.
        </p>

        <h3>LinkedTrust</h3>
        <p>
            <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>
            builds verified trust systems, civic tech platforms, and AI-powered tools
            for organizations that care about doing things right. Their work spans
            verifiable credentials, open-source development, and shared governance.
            Based in Tucson, Arizona, the LinkedTrust team focuses on political transparency,
            civic engagement, and trustworthy systems.
        </p>
    </section>

    <section>
        <h2>Our Data</h2>
        <p>
            Alonovo grades are built on claims — signed, URI-addressable statements
            with full provenance, following the
            <a href="https://identity.foundation/labs-linkedclaims/" target="_blank" rel="noreferrer">LinkedClaims</a>
            specification. Every grade links back to its source data so you can verify it yourself.
            We currently track <strong>17 values</strong> across <strong>335+ companies</strong>,
            drawn from these institutional sources:
        </p>

        <div class="source-grid">
            <div class="source-category">
                <h3>Corporate Governance</h3>
                <ul>
                    <li><a href="https://www.opensecrets.org" target="_blank" rel="noreferrer">OpenSecrets</a> — Corporate lobbying expenditures reported to Congress</li>
                    <li>S&amp;P Global — ESG (Environmental, Social, Governance) risk scores</li>
                    <li>Executive compensation data — CEO-to-median-worker pay ratios</li>
                    <li><a href="https://itep.org" target="_blank" rel="noreferrer">ITEP</a> — Institute on Taxation and Economic Policy (corporate tax fairness)</li>
                </ul>
            </div>

            <div class="source-category">
                <h3>Human Rights &amp; Labor</h3>
                <ul>
                    <li><a href="https://www.hrc.org/resources/corporate-equality-index" target="_blank" rel="noreferrer">Human Rights Campaign</a> — Corporate Equality Index (LGBTQ+ workplace equality)</li>
                    <li><a href="https://knowthechain.org" target="_blank" rel="noreferrer">KnowTheChain</a> — Supply chain forced labor benchmarks</li>
                    <li><a href="https://www.usaspending.gov" target="_blank" rel="noreferrer">USASpending.gov</a> — Federal contract data (ICE/CBP contracts)</li>
                    <li><a href="https://theintercept.com" target="_blank" rel="noreferrer">The Intercept</a> — ICE detention facility operators</li>
                </ul>
            </div>

            <div class="source-category">
                <h3>Animal Welfare</h3>
                <ul>
                    <li><a href="https://www.bbfaw.com" target="_blank" rel="noreferrer">BBFAW</a> — Business Benchmark on Farm Animal Welfare (tier ratings)</li>
                    <li><a href="https://www.eggtrack.com" target="_blank" rel="noreferrer">EggTrack</a> — Cage-free egg commitment progress</li>
                    <li><a href="https://www.peta.org" target="_blank" rel="noreferrer">PETA</a> — Cruelty-free certification (animal testing)</li>
                </ul>
            </div>

            <div class="source-category">
                <h3>Environment &amp; Public Safety</h3>
                <ul>
                    <li>GHG emissions data — Corporate greenhouse gas emissions reporting</li>
                    <li>Gun safety records — Corporate policies on firearm sales and safety</li>
                    <li>Tobacco involvement — Companies producing or distributing tobacco products</li>
                </ul>
            </div>
        </div>
    </section>

    <section>
        <h2>How We Grade</h2>
        <p>
            Each company is rated on the values above using data from the sources listed.
            Here's how it works:
        </p>
        <ol class="methodology">
            <li>
                <strong>Source data becomes a claim.</strong>
                Every fact we ingest (a lobbying amount, an ESG score, a cage-free percentage)
                is stored as a <a href="https://identity.foundation/labs-linkedclaims/" target="_blank" rel="noreferrer">LinkedClaim</a>
                — a signed statement with a source URL, date, and methodology you can inspect.
            </li>
            <li>
                <strong>Claims are scored per value.</strong>
                Each value has defined thresholds. For example, lobbying under $500K earns an A;
                over $10M earns an F. Cage-free egg commitments above 95% earn an A; below 25% earn an F.
                These rules are transparent and consistent.
            </li>
            <li>
                <strong>Values combine into an overall grade.</strong>
                By default, all values are weighted equally. If any "disqualifying" value
                (like operating an ICE detention facility) receives an F, the overall grade is F —
                no amount of good performance elsewhere can offset it.
            </li>
            <li>
                <strong>You can customize the weights.</strong>
                Care more about climate than CEO pay? Adjust the sliders.
                Your personalized grade recalculates instantly. Some values
                (like ICE involvement) have a minimum weight that can't be set to zero.
            </li>
        </ol>
        <p>
            The grade scale runs from A+ to F, with plus and minus gradations.
            Every grade on every company detail page links to the underlying claims
            so you can see exactly where the data came from.
        </p>
    </section>

    <section>
        <h2>Community</h2>
        <p>
            Anyone can contribute attested information about companies through the
            <a href="https://live.linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust community platform</a>.
            Community attestations are shown alongside institutional data on each company card.
        </p>
    </section>

    <section class="contact">
        <h2>Contact</h2>
        <p>
            For questions, feedback, or press inquiries, reach out through
            <a href="https://civ.works" target="_blank" rel="noreferrer">Civic Works</a>
            or
            <a href="https://linkedtrust.us" target="_blank" rel="noreferrer">LinkedTrust</a>.
        </p>
    </section>
</div>

<style>
    .about-page {
        max-width: 720px;
        margin: 0 auto;
    }

    .about-page h1 {
        color: #1a5f2a;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }

    .about-page h2 {
        color: #1a5f2a;
        font-size: 1.3rem;
        margin: 2rem 0 0.5rem;
    }

    .about-page h3 {
        color: #1a5f2a;
        font-size: 1.05rem;
        margin: 1.25rem 0 0.4rem;
    }

    .about-page p {
        line-height: 1.7;
        color: #333;
        margin: 0.5rem 0;
    }

    .about-page a {
        color: #1a5f2a;
    }

    .about-page ul {
        padding-left: 1.5rem;
        line-height: 1.8;
    }

    .about-page li {
        margin: 0.3rem 0;
    }

    section {
        margin-bottom: 1.5rem;
    }

    .source-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 1rem;
    }

    @media (max-width: 640px) {
        .source-grid {
            grid-template-columns: 1fr;
        }
    }

    .source-category {
        background: #f8faf8;
        border: 1px solid #e0e8e0;
        border-radius: 8px;
        padding: 1rem 1.25rem;
    }

    .source-category h3 {
        margin: 0 0 0.5rem;
        font-size: 0.95rem;
    }

    .source-category ul {
        padding-left: 1.2rem;
        line-height: 1.6;
        font-size: 0.9rem;
    }

    .source-category li {
        margin: 0.25rem 0;
    }

    .methodology {
        padding-left: 1.5rem;
        line-height: 1.7;
        counter-reset: none;
    }

    .methodology li {
        margin: 0.75rem 0;
    }

    .methodology li strong {
        color: #1a5f2a;
    }

    .contact {
        border-top: 1px solid #ddd;
        padding-top: 1.5rem;
        margin-top: 2rem;
    }
</style>
