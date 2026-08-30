/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#f0f2f5",
        card: "#ffffff",
        ink: "#101828",
        muted: "#98a2b3",
        accent: "#3b82f6",
        accent2: "#6366f1",
        danger: "#ef4444",
        warn: "#f59e0b",
        ok: "#22c55e",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
