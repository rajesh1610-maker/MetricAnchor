"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface AppNavProps {
  devMode?: boolean;
  onToggleDevMode?: () => void;
}

const NAV_LINKS = [
  { href: "/ask", label: "Ask" },
  { href: "/datasets", label: "Datasets" },
  { href: "/semantic-models", label: "Models" },
];

export default function AppNav({ devMode, onToggleDevMode }: AppNavProps) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        {/* Logo */}
        <div className="flex items-center gap-5">
          <Link href="/" className="flex items-center gap-2 group" aria-label="MetricAnchor home">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-anchor-500 shadow-sm group-hover:bg-anchor-400 transition-colors">
              <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-100 text-sm">MetricAnchor</span>
          </Link>

          {/* Nav links */}
          <nav className="flex items-center gap-1" aria-label="Main navigation">
            {NAV_LINKS.map(({ href, label }) => {
              const active = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    active
                      ? "bg-gray-800 text-gray-100"
                      : "text-gray-400 hover:bg-gray-800/60 hover:text-gray-200"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {onToggleDevMode !== undefined && (
            <button
              onClick={onToggleDevMode}
              title="Toggle developer mode (⌘⇧D)"
              aria-pressed={devMode}
              className={`rounded px-2.5 py-1 text-xs font-mono transition-colors border ${
                devMode
                  ? "border-anchor-600 bg-anchor-900/40 text-anchor-300"
                  : "border-gray-700 text-gray-600 hover:border-gray-600 hover:text-gray-400"
              }`}
            >
              DEV
            </button>
          )}
          <a
            href="/api/docs"
            className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            API
          </a>
          <a
            href="https://github.com/your-username/metricanchor"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="View on GitHub"
            className="text-gray-600 hover:text-gray-300 transition-colors"
          >
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
