import type { FeedbackResponse, InteractionTrace, QueryResponse } from "@/types/chat";
import { request } from "@/api/client";

export function submitQuery(query: string) {
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export function getInteractionTrace(interactionId: string) {
  return request<InteractionTrace>(`/interactions/${interactionId}/trace`);
}

export function submitRating(interactionId: string, rating: 1 | 2 | 3 | 4 | 5) {
  return request<FeedbackResponse>("/feedback", {
    method: "POST",
    body: JSON.stringify({ interaction_id: interactionId, rating }),
  });
}
