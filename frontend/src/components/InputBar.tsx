import { useState, useRef, type KeyboardEvent } from "react";
import { Send } from "lucide-react";

interface InputBarProps {
  onSend: (question: string) => void;
  loading: boolean;
}

export default function InputBar({ onSend, loading }: InputBarProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const q = value.trim();
    if (!q || loading) return;
    onSend(q);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  };

  return (
    <div className="input-bar">
      <textarea
        ref={textareaRef}
        className="input-textarea"
        rows={1}
        placeholder="Posez votre question sur le Code du numérique ou le Code général des impôts…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={loading}
      />
      <button
        className={`btn-send ${loading ? "btn-send--disabled" : ""}`}
        onClick={submit}
        disabled={loading || !value.trim()}
        aria-label="Envoyer"
      >
        <Send size={18} />
      </button>
    </div>
  );
}
