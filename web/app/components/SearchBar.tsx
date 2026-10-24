"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, Globe, ShieldCheck, Sparkles, X } from "lucide-react";
import { GlossaryTerm } from "../lib/types";

interface SearchBarProps {
  onSearch: (term: string, allowWebSearch: boolean) => void;
  isLoading: boolean;
  glossaryTerms: GlossaryTerm[];
}

const POPULAR_TERMS = [
  "RAG",
  "LLM",
  "Attention Mechanism",
  "Hallucination",
  "Diffusion Models",
  "Agentic AI",
  "Token",
  "Prompt",
];

export default function SearchBar({ onSearch, isLoading, glossaryTerms }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [allowWebSearch, setAllowWebSearch] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<GlossaryTerm[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length >= 1) {
      const lower = query.toLowerCase();
      const matches = glossaryTerms
        .filter((item) => item.key.includes(lower) || item.term.toLowerCase().includes(lower))
        .slice(0, 6);
      setFilteredSuggestions(matches);
      setShowSuggestions(matches.length > 0);
    } else {
      setFilteredSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query, glossaryTerms]);

  // Click outside listener to dismiss suggestions
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;
    setShowSuggestions(false);
    onSearch(query.trim(), allowWebSearch);
  };

  const selectSuggestion = (termName: string) => {
    setQuery(termName);
    setShowSuggestions(false);
    onSearch(termName, allowWebSearch);
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 mb-8" ref={wrapperRef}>
      <form onSubmit={handleSubmit} className="relative flex flex-col gap-3">
        {/* Input bar */}
        <div className="relative flex items-center">
          <div className="absolute left-4 text-slate-400 pointer-events-none">
            <Search className="w-5 h-5" />
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query.trim().length >= 1 && setShowSuggestions(true)}
            placeholder="Type any AI term (e.g. RAG, Attention Mechanism, Tokens)..."
            className="w-full clay-input pl-12 pr-32 py-4 text-base sm:text-lg font-medium text-slate-800 placeholder-slate-400 bg-white"
            disabled={isLoading}
          />

          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery("");
                setShowSuggestions(false);
              }}
              className="absolute right-28 text-slate-400 hover:text-slate-600 p-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-2 clay-btn clay-btn-primary px-5 py-2.5 text-sm sm:text-base font-bold disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center gap-1.5">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Thinking...
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                Explain
              </span>
            )}
          </button>
        </div>

        {/* Autocomplete Dropdown */}
        {showSuggestions && filteredSuggestions.length > 0 && (
          <div className="absolute top-16 left-0 right-0 z-30 clay-card bg-white/95 backdrop-blur-md p-2 mt-1 max-h-64 overflow-y-auto shadow-2xl">
            <div className="text-[11px] font-bold text-slate-400 px-3 py-1 uppercase tracking-wider">
              Glossary Matches
            </div>
            {filteredSuggestions.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => selectSuggestion(item.term)}
                className="w-full text-left px-3 py-2 rounded-xl hover:bg-indigo-50 transition flex flex-col group"
              >
                <div className="text-sm font-bold text-slate-800 group-hover:text-indigo-600">
                  {item.term}
                </div>
                <div className="text-xs text-slate-500 line-clamp-1">
                  {item.definition}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Popular Term Quick Pills & Web Search Toggle */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-1 pt-1">
          {/* Quick pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-400 mr-1">Trending:</span>
            {POPULAR_TERMS.map((term) => (
              <button
                key={term}
                type="button"
                onClick={() => selectSuggestion(term)}
                disabled={isLoading}
                className="clay-pill px-3 py-1 bg-white hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 text-xs transition disabled:opacity-50"
              >
                {term}
              </button>
            ))}
          </div>

          {/* Safe Web Search Toggle */}
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <div className="relative">
              <input
                type="checkbox"
                checked={allowWebSearch}
                onChange={(e) => setAllowWebSearch(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
            </div>
            <span className="text-xs font-semibold text-slate-600 flex items-center gap-1">
              <Globe className="w-3.5 h-3.5 text-indigo-500" />
              Safe Web Search
            </span>
          </label>
        </div>
      </form>
    </div>
  );
}
