"use client";

import React, { useState } from "react";
import { X, BookOpen, Search, Sparkles } from "lucide-react";
import { GlossaryTerm } from "../lib/types";

interface GlossaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  terms: GlossaryTerm[];
  onSelectTerm: (term: string) => void;
}

export default function GlossaryModal({
  isOpen,
  onClose,
  terms,
  onSelectTerm,
}: GlossaryModalProps) {
  const [filter, setFilter] = useState("");

  if (!isOpen) return null;

  const filtered = terms.filter(
    (t) =>
      t.term.toLowerCase().includes(filter.toLowerCase()) ||
      t.definition.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="clay-card p-6 sm:p-8 max-w-2xl w-full bg-white relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Official AI Glossary
              </h3>
              <p className="text-xs text-slate-500">
                Stanford Institute for Human-Centered AI (HAI) • {terms.length} verified terms
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search bar inside modal */}
        <div className="my-4 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search glossary definitions (e.g. alignment, transformer)..."
            className="w-full clay-input pl-9 pr-4 py-2.5 text-xs sm:text-sm font-medium text-slate-800 bg-slate-50"
          />
        </div>

        {/* Terms list */}
        <div className="overflow-y-auto flex-1 pr-1 space-y-3">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              No matching glossary terms found.
            </div>
          ) : (
            filtered.map((t) => (
              <div
                key={t.key}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-emerald-300 transition group flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-slate-900 group-hover:text-emerald-700">
                    {t.term}
                  </h4>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {t.definition}
                  </p>
                </div>

                <button
                  onClick={() => {
                    onSelectTerm(t.term);
                    onClose();
                  }}
                  className="clay-btn clay-btn-accent px-3 py-1.5 text-xs font-bold shrink-0 self-start sm:self-center"
                >
                  <Sparkles className="w-3 h-3 mr-1" />
                  Explain
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
