import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0F19",
        foreground: "#E5E7EB",
        primary: {
          DEFAULT: "#F5C542",
          foreground: "#0B0F19"
        },
        muted: "#111827",
        card: "#111827",
        border: "rgba(255,255,255,0.08)",
        secondary: "#E5E7EB",
        hover: "#F5D76E",
        "muted-foreground": "#9CA3AF",
      },
      boxShadow: {
        glow: "0 0 25px rgba(245,197,66,0.12)",
        "glow-lg": "0 0 40px rgba(245,197,66,0.16)",
        card: "0 4px 24px rgba(0,0,0,0.3)",
      },
      borderRadius: {
        lg: "0.9rem",
        md: "0.65rem",
        sm: "0.45rem"
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in": {
          "0%": { opacity: "0", transform: "translateX(-12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        heartbeat: {
          "0%, 100%": { transform: "scale(1)", opacity: "1" },
          "50%": { transform: "scale(1.15)", opacity: "0.7" },
        },
        "progress-fill": {
          "0%": { width: "0%" },
          "100%": { width: "var(--target-width)" },
        },
        "check-pop": {
          "0%": { transform: "scale(0)", opacity: "0" },
          "60%": { transform: "scale(1.2)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s ease-out forwards",
        "fade-in-delay-1": "fade-in 0.4s ease-out 0.1s forwards",
        "fade-in-delay-2": "fade-in 0.4s ease-out 0.2s forwards",
        "fade-in-delay-3": "fade-in 0.4s ease-out 0.3s forwards",
        "slide-in": "slide-in 0.35s ease-out forwards",
        "scale-in": "scale-in 0.3s ease-out forwards",
        heartbeat: "heartbeat 1.5s ease-in-out infinite",
        "check-pop": "check-pop 0.35s ease-out forwards",
      },
    }
  },
  plugins: []
};

export default config;
