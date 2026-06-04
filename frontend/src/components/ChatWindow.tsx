import type { RefObject } from "react";
import type { Message } from "../types";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
  bottomRef: RefObject<HTMLDivElement>;
}

export default function ChatWindow({ messages, loading, bottomRef }: ChatWindowProps) {
  return (
    <div className="chat-window">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
