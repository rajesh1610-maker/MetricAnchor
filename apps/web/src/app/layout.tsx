import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MetricAnchor — Grounded answers for business data",
  description:
    "Trust-first AI analytics copilot. Upload data, define business metrics, ask questions in natural language, and inspect every answer.",
  openGraph: {
    title: "MetricAnchor",
    description: "Grounded answers for business data.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full bg-white">{children}</body>
    </html>
  );
}
