import Link from "next/link";

const TRUST_PILLARS = [
  {
    label: "Generated SQL",
    desc: "The exact query that ran. Always visible — never hidden behind a loading spinner.",
    icon: (
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
  },
  {
    label: "Term mappings",
    desc: 'Every business word traced to its source. "Revenue" is always the same calculation.',
    icon: (
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z" />
      </svg>
    ),
  },
  {
    label: "Assumptions declared",
    desc: '"Last month" → Feb 1–28. Every inference is shown, not guessed silently.',
    icon: (
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
  },
  {
    label: "Confidence level",
    desc: "High / Medium / Low — with a plain-English explanation so you know when to trust it.",
    icon: (
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
];

const HOW_IT_WORKS = [
  {
    n: "01",
    title: "Upload your data",
    desc: "Drag in a CSV or Parquet file. MetricAnchor profiles the schema automatically.",
  },
  {
    n: "02",
    title: "Define your metrics",
    desc: 'Use the guided wizard or YAML editor to define what "revenue", "churn", and "AOV" mean for your dataset.',
  },
  {
    n: "03",
    title: "Ask in plain English",
    desc: "Every answer comes with its SQL, term mappings, assumptions, and a confidence score.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Nav */}
      <nav className="sticky top-0 z-10 border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-anchor-500">
              <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-100">MetricAnchor</span>
          </div>
          <div className="flex items-center gap-5">
            <Link href="/ask" className="text-sm text-gray-400 hover:text-gray-100 transition-colors">Ask</Link>
            <Link href="/datasets" className="text-sm text-gray-400 hover:text-gray-100 transition-colors">Datasets</Link>
            <Link href="/semantic-models" className="text-sm text-gray-400 hover:text-gray-100 transition-colors">Models</Link>
            <a
              href="https://github.com/your-username/metricanchor"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="px-6 pt-24 pb-20">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-anchor-800 bg-anchor-950/50 px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-anchor-400 animate-pulse" aria-hidden />
            <span className="text-xs font-medium text-anchor-300">
              Open source · Local-first · Trust-first
            </span>
          </div>

          <h1 className="text-5xl font-bold tracking-tight text-gray-50 leading-tight mb-6">
            AI analytics that shows
            <br />
            <span className="text-anchor-400">its work.</span>
          </h1>

          <p className="mx-auto mb-10 max-w-xl text-lg text-gray-400 leading-relaxed">
            Upload a CSV, define your business metrics, ask questions in plain English.
            Every answer includes the SQL, term mappings, assumptions, and a confidence level.
            <strong className="text-gray-200"> No black boxes.</strong>
          </p>

          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/datasets/upload"
              className="rounded-lg bg-anchor-500 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-anchor-400 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-anchor-400"
            >
              Upload your data
            </Link>
            <Link
              href="/ask"
              className="rounded-lg border border-gray-700 px-6 py-3 text-sm font-semibold text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
            >
              Start asking questions
            </Link>
          </div>
        </div>
      </section>

      {/* Answer preview mockup */}
      <section className="px-6 pb-20">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-2xl border border-gray-800 bg-gray-900 overflow-hidden shadow-2xl">
            <div className="px-5 py-4 border-b border-gray-800 bg-gray-900/60">
              <p className="text-xs text-gray-500 mb-1">Question</p>
              <p className="text-sm text-gray-200 font-medium">What was revenue last month by product category?</p>
            </div>
            <div className="px-5 py-4 border-b border-gray-800">
              <p className="text-gray-100 text-sm leading-relaxed">
                Revenue last month totalled <strong className="text-anchor-300">$42,750</strong> across 3 categories.
                Electronics led with $21,200, followed by Apparel at $14,550 and Home at $7,000.
              </p>
              <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-green-700 bg-green-900/30 px-2.5 py-0.5 text-xs text-green-300">
                High confidence — All terms mapped exactly
              </div>
            </div>
            <div className="px-5 py-3 flex gap-4 text-xs border-b border-gray-800 bg-gray-900/40">
              {["Answer", "Chart", "Table", "SQL", "Assumptions", "Provenance"].map((tab, i) => (
                <span key={tab} className={i === 0 ? "text-anchor-400 border-b border-anchor-400 pb-0.5" : "text-gray-600"}>{tab}</span>
              ))}
            </div>
            <div className="px-5 py-3 bg-gray-950/60">
              <pre className="text-xs font-mono text-gray-400 leading-relaxed overflow-x-auto">
{`SELECT
  "product_category" AS product_category,
  SUM(order_total) FILTER(WHERE status = 'completed') AS revenue
FROM "retail_sales"
WHERE "order_date" >= '2026-02-01'
  AND "order_date" < '2026-03-01'
GROUP BY "product_category"
ORDER BY revenue DESC`}
              </pre>
            </div>
          </div>
          <p className="mt-3 text-center text-xs text-gray-600">
            SQL, term mappings, assumptions, and confidence — on every answer.
          </p>
        </div>
      </section>

      {/* Trust pillars */}
      <section className="border-y border-gray-800 bg-gray-900/40 px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <p className="mb-8 text-center text-xs font-semibold uppercase tracking-widest text-gray-500">
            Every answer includes
          </p>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {TRUST_PILLARS.map((p) => (
              <div key={p.label} className="rounded-xl border border-gray-800 bg-gray-900 p-5">
                <div className="mb-3 text-anchor-400">{p.icon}</div>
                <h3 className="mb-1.5 text-sm font-semibold text-gray-100">{p.label}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-2xl font-bold text-gray-100">How it works</h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {HOW_IT_WORKS.map((step) => (
              <div key={step.n} className="relative">
                <div className="mb-3 text-3xl font-bold text-gray-800 font-mono">{step.n}</div>
                <h3 className="mb-2 text-sm font-semibold text-gray-100">{step.title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* For both users */}
      <section className="border-t border-gray-800 px-6 py-16 bg-gray-900/40">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-8 text-center text-xl font-bold text-gray-100">Built for two kinds of users</h2>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-7">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-blue-900/30 border border-blue-800 px-3 py-1 text-xs font-semibold text-blue-300">
                Citizen Developer
              </div>
              <h3 className="mb-2 text-base font-semibold text-gray-100">Maya — Marketing Analyst</h3>
              <p className="mb-5 text-sm text-gray-400 leading-relaxed">
                Uploads a CSV, defines "revenue" once, and gets trustworthy answers every Monday
                without filing a data request or writing SQL.
              </p>
              <ul className="space-y-2">
                {["Drag-and-drop CSV upload", "Auto schema profiling", "Guided metric wizard", "Ask questions, get charts", "One-click feedback on wrong answers"].map((f) => (
                  <li key={f} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="mt-0.5 text-green-500 shrink-0">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-7">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-purple-900/30 border border-purple-800 px-3 py-1 text-xs font-semibold text-purple-300">
                Analytics Engineer
              </div>
              <h3 className="mb-2 text-base font-semibold text-gray-100">Dev — Analytics Engineer</h3>
              <p className="mb-5 text-sm text-gray-400 leading-relaxed">
                Edits YAML semantic models, inspects the full pipeline trace, runs tests,
                and validates definitions against JSON schema.
              </p>
              <ul className="space-y-2">
                {["YAML semantic models + JSON schema validation", "Provider-agnostic LLM (OpenAI, Anthropic, Ollama)", "Developer mode with pipeline trace", "REST API with OpenAPI docs", "pytest integration test suite"].map((f) => (
                  <li key={f} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="mt-0.5 text-green-500 shrink-0">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Quick start */}
      <section className="px-6 py-16 border-t border-gray-800">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-2 text-xl font-bold text-gray-100">Up in 5 minutes</h2>
          <p className="mb-8 text-sm text-gray-500">No cloud account. No managed database. Just Docker.</p>
          <div className="overflow-hidden rounded-xl bg-gray-900 border border-gray-800 text-left">
            <div className="flex items-center gap-1.5 border-b border-gray-800 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-red-500/60" aria-hidden />
              <span className="h-3 w-3 rounded-full bg-yellow-500/60" aria-hidden />
              <span className="h-3 w-3 rounded-full bg-green-500/60" aria-hidden />
              <span className="ml-2 text-xs text-gray-600">Terminal</span>
            </div>
            <pre className="overflow-x-auto px-5 py-5 font-mono text-sm leading-7 text-gray-300">
              <code>{`git clone https://github.com/your-username/metricanchor
cd metricanchor
cp .env.example .env   # add your LLM API key
make up && make seed
open http://localhost:3000`}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 px-6 py-8">
        <div className="mx-auto flex max-w-6xl items-center justify-between text-xs text-gray-600">
          <span>MetricAnchor — Apache 2.0</span>
          <div className="flex gap-5">
            <Link href="/api/docs" className="hover:text-gray-400">API Docs</Link>
            <a href="https://github.com/your-username/metricanchor" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
