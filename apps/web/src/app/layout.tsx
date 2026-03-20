import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

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
    <html lang="en" className={`h-full ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="h-full bg-white font-sans">{children}</body>
    </html>
  );
}
