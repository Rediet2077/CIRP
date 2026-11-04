import { createFetch } from "@better-fetch/fetch";
import { z } from "zod";
import { localStorageService } from "./local_storage";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? window.location.origin + "/api" : "/api");

interface AuthSession {
  access: string;
  refresh: string;
}

function getAuthToken(): string | undefined {
  const session = localStorageService.getItem<AuthSession>("authSession");
  return session?.access;
}

const betterFetchClient = createFetch({
  baseURL: API_BASE_URL,
  retry: {
    type: "linear",
    attempts: 1,
    delay: 500,
  },
});

export async function executeApiRequest<T>(options: {
  endpoint: string;
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  outputSchema: z.ZodType<T>;
  mockFallback?: () => T | Promise<T>;
}): Promise<T> {
  const { endpoint, method = "GET", body, query, outputSchema, mockFallback } = options;

  const hasConfiguredExternalApi = Boolean(
    process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL.length > 0
  );

  if (hasConfiguredExternalApi) {
    try {
      const token = getAuthToken();
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // Use regular fetch instead of better-fetch
      // Simple URL construction: base + endpoint
      const baseUrl = API_BASE_URL.replace(/\/$/, ''); // Remove trailing slash
      const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
      const fullUrl = `${baseUrl}${cleanEndpoint}`;
      
      const url = new URL(fullUrl);
      
      if (query) {
        Object.entries(query).forEach(([key, value]) => {
          if (value !== undefined) {
            url.searchParams.append(key, String(value));
          }
        });
      }

      console.log('🌐 API Request:', method, url.toString());
      
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      console.log('📥 API Response:', response.status, response.statusText);

      if (!response.ok) {
        // Handle 401 Unauthorized by redirecting to login
        if (response.status === 401 && typeof window !== 'undefined') {
          console.log('🔐 Unauthorized - redirecting to login');
          window.location.href = '/login';
          // Return empty data to prevent further errors during redirect
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const rawData = await response.json();
      console.log('📦 Raw data received:', rawData);
      
      const validatedData = outputSchema.parse(rawData);
      console.log('✅ Data validated successfully');
      
      return validatedData;
    } catch (error) {
      console.error('❌ API Request failed:', error);
      // A configured backend is authoritative. Falling back here can make a
      // failed write look successful and show stale or unscoped mock records.
      throw error;
    }
  }

  if (mockFallback) {
    const fallbackResult = await mockFallback();
    return outputSchema.parse(fallbackResult);
  }

  throw new Error(`API endpoint ${endpoint} failed and no fallback was provided.`);
}
