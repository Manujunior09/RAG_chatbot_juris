import { useState } from "react";
import { ChevronDown, ChevronUp, FileText } from "lucide-react";
import type { SourceItem } from "../types";

interface SourcesListProps {
  sources: SourceItem[];
}

export default function SourcesList({ sources }: SourcesListProps) {
  const [open, setOpen] = useState(false);

  if (!sources.length) return null;

  return (
    <div className="sources-wrapper">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        <FileText size={13} />
        {sources.length} source{sources.length > 1 ? "s" : ""} consultée{sources.length > 1 ? "s" : ""}
        {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>
      {open && (
        <ul className="sources-list">
          {sources.map((s, i) => (
            <li key={i} className="source-item">
              <div className="source-header">
                <span className="source-doc">{s.document}</span>
                <span className="source-score">{Math.round(s.score * 100)}%</span>
              </div>
              <p className="source-extrait">{s.extrait}…</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
