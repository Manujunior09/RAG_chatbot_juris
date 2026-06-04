import { motion } from "framer-motion";
import { Scale, User } from "lucide-react";
import type { Message } from "../types";
import SourcesList from "./SourcesList";

interface MessageBubbleProps {
  message: Message;
}

function formatText(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      className={`bubble-row ${isUser ? "bubble-row--user" : "bubble-row--bot"}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.400, ease: "easeOut" }}
    >
      {!isUser && (
        <div className="avatar avatar--bot">
          <Scale size={16} />
        </div>
      )}

      <div className={`bubble ${isUser ? "bubble--user" : "bubble--bot"}`}>
        <p
          className="bubble-text"
          dangerouslySetInnerHTML={{ __html: formatText(message.text) }}
        />

        {message.sources && <SourcesList sources={message.sources} />}

        {message.times && (
          <div className="bubble-times">
            🔍 {message.times.retrieval} ms &nbsp;|&nbsp;
            💬 {message.times.llm} ms &nbsp;|&nbsp;
            ⏱️ {message.times.total} ms
          </div>
        )}
      </div>

      {isUser && (
        <div className="avatar avatar--user">
          <User size={16} />
        </div>
      )}
    </motion.div>
  );
}
