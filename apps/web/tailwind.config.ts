import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        anchor: {
          50:  "#f0f4ff",
          100: "#e0e9ff",
          200: "#c7d6fe",
          500: "#4f6ef7",
          600: "#3b55e6",
          700: "#2d42cc",
          900: "#1a2680",
        },
      },
    },
  },
  plugins: [],
};

export default config;
