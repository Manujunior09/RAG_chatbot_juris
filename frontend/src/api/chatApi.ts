import type { AskResponse } from "../types";

const BASE = "/api";

export async function createSession(): Promise<string> {
  const res = await fetch(`${BASE}/session`, { method: "POST" });
  if (!res.ok) throw new Error("Impossible de créer une session");
  const data = await res.json();
  return data.session_id;
}

export async function askQuestion(
  question: string,
  session_id: string
): Promise<AskResponse> {
  const res = await fetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id }),
  });
  if (!res.ok) throw new Error("Erreur lors de la requête");
  return res.json();
}
