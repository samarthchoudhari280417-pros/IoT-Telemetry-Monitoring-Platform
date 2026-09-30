import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        panel: "#121820",
        border: "#232b36",
        accent: "#3ddc97",
        warn: "#f5a524",
        danger: "#f5556c",
        muted: "#8a97a6",
      },
    },
  },
  plugins: [],
};
export default config;
