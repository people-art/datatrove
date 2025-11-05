"use client";

import { X } from "lucide-react";
import { useState } from "react";

interface KeywordInputProps {
  value?: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  maxKeywords?: number;
}

export function KeywordInput({
  value = [],
  onChange,
  placeholder = "Add relevant keywords…",
  maxKeywords = 64
}: KeywordInputProps) {
  const [input, setInput] = useState("");

  const commitKeywords = (raw: string) => {
    const items = raw.split(/[,\n]/).map(s => s.trim()).filter(Boolean);
    if (!items.length) return;

    const set = new Set([...(value || []), ...items]);
    const newValue = Array.from(set).slice(0, maxKeywords);
    onChange(newValue);
    setInput("");
  };

  const removeKeyword = (keyword: string) => {
    onChange((value || []).filter(k => k !== keyword));
  };

  const keywordCount = (value || []).length;
  const hasError = maxKeywords > 0 && keywordCount >= maxKeywords;

  return (
    <div
      className="rounded-2xl border border-line bg-background p-3 focus-within:border-primary/50 transition-colors"
      role="group"
      aria-label="Keyword input"
    >
      <div className="flex flex-wrap gap-2">
        {(value || []).map((keyword, index) => (
          <span
            key={keyword}
            className="inline-flex items-center gap-1.5 rounded-lg bg-foreground/5 px-2.5 py-1 text-sm hover:bg-foreground/10 transition-colors"
          >
            {keyword}
            <button
              type="button"
              aria-label={`Remove keyword: ${keyword}`}
              onClick={() => removeKeyword(keyword)}
              className="text-foreground/60 hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50 focus:rounded-sm"
            >
              <X className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          </span>
        ))}

        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === "Enter" || e.key === "Tab" || e.key === ",") {
              e.preventDefault();
              commitKeywords(input);
            }
          }}
          onPaste={e => {
            const text = e.clipboardData.getData("text");
            if (text.includes(",") || text.includes("\n")) {
              e.preventDefault();
              commitKeywords(text);
            }
          }}
          placeholder={(value || []).length === 0 ? placeholder : ""}
          className="flex-1 min-w-[160px] bg-transparent outline-none h-7 placeholder:text-foreground/40"
          aria-describedby="keyword-help keyword-count"
          aria-invalid={hasError}
          aria-label="Enter keywords"
        />
      </div>

      <div className="flex justify-between items-center mt-2">
        <div id="keyword-help" className="sr-only">
          Enter keywords separated by commas, or paste a comma-separated list
        </div>
        <div
          id="keyword-count"
          className="text-xs text-foreground/60"
          aria-live="polite"
        >
          {keywordCount} keyword{keywordCount !== 1 ? 's' : ''} added
          {maxKeywords > 0 && ` (max ${maxKeywords})`}
        </div>
      </div>
    </div>
  );
}
