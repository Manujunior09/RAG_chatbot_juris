export interface SourceItem {
  document: string;
  chunk_index: number;
  score: number;
  extrait: string;
}

export interface AskResponse {
  reponse: string;
  sources: SourceItem[];
  temps_retrieval_ms: number;
  temps_llm_ms: number;
  temps_total_ms: number;
  session_id: string;
  nb_chunks_trouves: number;
  question: string;
}

export type Role = "user" | "bot";

export interface Message {
  id: string;
  role: Role;
  text: string;
  sources?: SourceItem[];
  times?: {
    retrieval: number;
    llm: number;
    total: number;
  };
}
