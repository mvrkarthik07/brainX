import type { APIErrorPayload } from "@/types/api";

const configuredBaseUrl = import.meta.env.VITE_BRAINX_API_BASE_URL?.trim();

export const BASE_URL = configuredBaseUrl || "http://localhost:8420";
const FALLBACK_BASE_URLS = configuredBaseUrl
  ? [configuredBaseUrl]
  : ["http://localhost:8420", "http://127.0.0.1:8420", "http://localhost:8000", "http://127.0.0.1:8000"];

let lastHealthyBaseUrl = BASE_URL;

export class APIError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

async function parseError(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as APIErrorPayload;
    return payload.detail ?? response.statusText;
  }
  return response.text();
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers ?? {});
  if (!(options?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let networkError: unknown = null;

  for (const baseUrl of [lastHealthyBaseUrl, ...FALLBACK_BASE_URLS.filter((url) => url !== lastHealthyBaseUrl)]) {
    try {
      const response = await fetch(`${baseUrl}${path}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new APIError(response.status, await parseError(response));
      }

      lastHealthyBaseUrl = baseUrl;

      if (response.status === 204) {
        return undefined as T;
      }

      return (await response.json()) as T;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      networkError = error;
    }
  }

  throw new APIError(0, networkError instanceof Error ? networkError.message : "Unable to reach the BrainX API");
}
