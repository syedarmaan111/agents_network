import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    server: {
        // Bind to IPv4 as well as localhost so the app works in Chrome with
        // http://127.0.0.1:5173 and not only VS Code's browser preview.
        host: "0.0.0.0",
    },
});
