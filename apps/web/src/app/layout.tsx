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
      <body className="h-full bg-white">{children}</body>
    </html>
  );
}
