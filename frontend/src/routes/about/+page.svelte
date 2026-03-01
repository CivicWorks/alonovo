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
            specification. We ingest data from institutional sources including:
        </p>
        <ul>
            <li><a href="https://www.opensecrets.org" target="_blank" rel="noreferrer">OpenSecrets</a> — Corporate lobbying expenditures</li>
            <li><a href="https://www.bbfaw.com" target="_blank" rel="noreferrer">BBFAW</a> — Business Benchmark on Farm Animal Welfare</li>
            <li><a href="https://www.eggtrack.com" target="_blank" rel="noreferrer">EggTrack</a> — Cage-free egg commitments</li>
            <li><a href="https://www.usaspending.gov" target="_blank" rel="noreferrer">USASpending</a> — Federal contract data (including ICE)</li>
            <li>S&amp;P Global — ESG risk scores</li>
        </ul>
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

    .contact {
        border-top: 1px solid #ddd;
        padding-top: 1.5rem;
        margin-top: 2rem;
    }
</style>
