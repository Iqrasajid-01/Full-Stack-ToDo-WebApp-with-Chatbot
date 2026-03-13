import { createAuthClient } from "better-auth/client";
import { cookies } from "next/headers";

export const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  fetchOptions: {
    headers: {
      "Content-Type": "application/json",
    },
  },
  // Add any other configuration options
});