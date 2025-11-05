'use client';

import { useState, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { X } from 'lucide-react';

interface KeywordInputProps {
  keywords: string[];
  onChange: (keywords: string[]) => void;
  placeholder?: string;
}

export function KeywordInput({ keywords, onChange, placeholder = "Add keyword..." }: KeywordInputProps) {
  const [inputValue, setInputValue] = useState('');

  const addKeyword = (keyword: string) => {
    const trimmed = keyword.trim();
    if (trimmed && !keywords.includes(trimmed)) {
      onChange([...keywords, trimmed]);
    }
    setInputValue('');
  };

  const removeKeyword = (keywordToRemove: string) => {
    onChange(keywords.filter(k => k !== keywordToRemove));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (inputValue.includes(',')) {
        // Handle comma-separated input
        const newKeywords = inputValue.split(',').map(k => k.trim()).filter(k => k);
        const uniqueNewKeywords = newKeywords.filter(k => !keywords.includes(k));
        if (uniqueNewKeywords.length > 0) {
          onChange([...keywords, ...uniqueNewKeywords]);
        }
        setInputValue('');
      } else {
        addKeyword(inputValue);
      }
    } else if (e.key === ',') {
      e.preventDefault();
      addKeyword(inputValue);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2 min-h-[40px] p-2 border rounded-md">
        {keywords.map((keyword) => (
          <span
            key={keyword}
            className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-sm"
          >
            {keyword}
            <button
              onClick={() => removeKeyword(keyword)}
              className="hover:bg-blue-200 rounded-full p-0.5"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={keywords.length === 0 ? placeholder : ""}
          className="flex-1 min-w-[120px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0 p-0 h-auto"
        />
      </div>
      <p className="text-xs text-gray-500">
        Press Enter or comma to add keywords. You can paste multiple keywords separated by commas.
      </p>
    </div>
  );
}
