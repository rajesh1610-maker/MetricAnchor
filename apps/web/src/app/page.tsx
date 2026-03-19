export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="border-b border-gray-100 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-anchor-600">
              <svg
                className="h-4 w-4 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <span className="text-base font-semibold text-gray-900">MetricAnchor</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/your-username/metricanchor"
              className="text-sm text-gray-500 hover:text-gray-900"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a href="/api/docs" className="text-sm text-gray-500 hover:text-gray-900">
              API Docs
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="px-6 py-20 text-center">
        <div className="mx-auto max-w-3xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-anchor-200 bg-anchor-50 px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-anchor-600" />
            <span className="text-xs font-medium text-anchor-700">Open source · Local-first · Trust-first</span>
          </div>

          <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900">
            Grounded answers for
            <br />
            <span className="text-anchor-600">business data.</span>
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-xl text-gray-500">
            Upload a CSV, define your business metrics, and ask questions in plain English.
            Every answer shows its SQL, assumptions, and confidence level.{" "}
            <strong className="text-gray-700">No black boxes.</strong>
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="https://github.com/your-username/metricanchor"
              className="inline-flex items-center gap-2 rounded-lg bg-anchor-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-anchor-700"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
            <a
              href="/api/docs"
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >
              Explore the API
            </a>
          </div>
        </div>
      </section>

      {/* Trust demo strip */}
      <section className="border-y border-gray-100 bg-gray-50 px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <p className="mb-10 text-center text-sm font-semibold uppercase tracking-widest text-gray-400">
            Every answer includes
          </p>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: "💾",
                title: "Generated SQL",
                desc: "The exact query that ran against your data. Always visible, never hidden.",
              },
              {
                icon: "🏷️",
                title: "Term mappings",
                desc: 'Which semantic model definitions were applied. "Revenue" always means the same thing.',
              },
              {
                icon: "📋",
                title: "Assumptions",
                desc: '"Last quarter" interpreted as Q4 2025. Date ranges, filters, and logic — all declared.',
              },
              {
                icon: "📊",
                title: "Confidence level",
                desc: "High, Medium, Low, or Unsure — with a plain-English explanation of why.",
              },
            ].map((item) => (
              <div key={item.title} className="rounded-xl border border-gray-200 bg-white p-5">
                <div className="mb-3 text-2xl">{item.icon}</div>
                <h3 className="mb-1.5 font-semibold text-gray-900">{item.title}</h3>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">
            Built for two kinds of users
          </h2>
          <div className="grid gap-8 lg:grid-cols-2">
            <div className="rounded-2xl border border-gray-100 p-8 shadow-sm">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                Citizen Developer
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Maya — Marketing Analyst
              </h3>
              <p className="mb-5 text-gray-500">
                Uploads a CSV, defines "revenue" once, and gets trustworthy answers every Monday
                morning — without filing a data request or writing SQL.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                {[
                  "Upload CSV or Parquet files via drag-and-drop",
                  "Auto-generated schema profile",
                  "Define metrics in plain English via UI",
                  "Ask questions, get charts and tables",
                  "Flag wrong answers with one click",
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <span className="mt-0.5 text-green-500">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-gray-100 p-8 shadow-sm">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700">
                Analytics Engineer
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Dev — Analytics Engineer
              </h3>
              <p className="mb-5 text-gray-500">
                Edits YAML semantic models in code, inspects the full LLM prompt, writes tests, and
                contributes connectors to the OSS project.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                {[
                  "YAML semantic models with JSON schema validation",
                  "CLI: upload, validate, ask",
                  "Full LLM prompt visible in developer view",
                  "REST API with OpenAPI docs",
                  "pytest suite + Playwright smoke tests",
                ].map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <span className="mt-0.5 text-green-500">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Quick start */}
      <section className="border-t border-gray-100 bg-gray-950 px-6 py-16 text-white">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="mb-4 text-2xl font-bold">Up in under 5 minutes</h2>
          <p className="mb-8 text-gray-400">
            No database to configure. No cloud account required. Just Docker.
          </p>
          <div className="overflow-hidden rounded-xl bg-gray-900 text-left">
            <div className="flex items-center gap-1.5 border-b border-gray-800 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-red-500/70" />
              <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
              <span className="h-3 w-3 rounded-full bg-green-500/70" />
              <span className="ml-2 text-xs text-gray-500">Terminal</span>
            </div>
            <pre className="overflow-x-auto px-5 py-5 font-mono text-sm leading-7 text-gray-300">
              <code>{`git clone https://github.com/your-username/metricanchor
cd metricanchor
cp .env.example .env   # add your LLM API key
make up
make seed              # load demo datasets
open http://localhost:3000`}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Status banner */}
      <section className="border-t border-gray-100 bg-amber-50 px-6 py-6">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm text-amber-800">
            <strong>Phase 1 of 6</strong> — Repository scaffold is complete. File upload, Q&A
            engine, and the full UI are coming in Phases 2–5.{" "}
            <a
              href="https://github.com/your-username/metricanchor"
              className="underline underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
            >
              Watch the repo
            </a>{" "}
            to follow progress.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 px-6 py-8">
        <div className="mx-auto flex max-w-6xl items-center justify-between text-sm text-gray-400">
          <span>MetricAnchor — Apache 2.0</span>
          <div className="flex gap-6">
            <a href="/api/docs" className="hover:text-gray-700">API Docs</a>
            <a
              href="https://github.com/your-username/metricanchor"
              className="hover:text-gray-700"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
