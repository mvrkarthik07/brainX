import type { BrainXHealthResponse } from "@/types/api";
import { request } from "@/api/client";

export function getHealth() {
  return request<BrainXHealthResponse>("/health");
}
