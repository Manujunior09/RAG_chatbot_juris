import { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import type { Message } from "../types";
import { createSession, askQuestion } from "../api/chatApi";

const WELCOME: Message = {
  id: "welcome",
  role: "bot",
  text: "Bonjour ! Je réponds aux questions à partir du **Code du numérique** et du **Code général des impôts** en République du Bénin.",
};

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [sessionId, setSessionId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    createSession().then(setSessionId).catch(console.error);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (question: string) => {
    if (!question.trim() || loading) return;

    setMessages((prev) => [
      ...prev,
      { id: uuidv4(), role: "user", text: question },
    ]);
    setLoading(true);

    try {
      const data = await askQuestion(question, sessionId);
      setMessages((prev) => [
        ...prev,
        {
          id: uuidv4(),
          role: "bot",
          text: data.reponse,
          sources: data.sources,
          times: {
            retrieval: data.temps_retrieval_ms,
            llm: data.temps_llm_ms,
            total: data.temps_total_ms,
          },
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: uuidv4(), role: "bot", text: "⚠️ Une erreur est survenue. Veuillez réessayer." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const newConversation = async () => {
    const sid = await createSession();
    setSessionId(sid);
    setMessages([
      WELCOME,
      { id: uuidv4(), role: "bot", text: "Nouvelle conversation démarrée. Comment puis-je vous aider ?" },
    ]);
  };

  return { messages, loading, send, newConversation, bottomRef };
}
