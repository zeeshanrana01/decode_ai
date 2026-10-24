"use client";

import React, { useState } from "react";
import { Globe, ShieldAlert, Check, X, Search } from "lucide-react";
import { HitlPromptData } from "../lib/types";

interface HitlModalProps {
  data: HitlPromptData | null;
  onDecision: (requestId: string, decision: "approve" | "reject", editedQuery?: string) => void;
  onClose: () => void;
}

export default function HitlModal({ data, onDecision, onClose }: HitlModalProps) {
  const [editedQuery, setEditedQuery] = useState("");

  if (!data) return null;

  const currentQuery = editedQuery || data.query;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="clay-card p-6 sm:p-8 max-w-lg w-full bg-white relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
            <Globe className="w-6 h-6 animate-spin-slow" />
          </div>
          <div>
            <span className="text-[11px] font-black uppercase tracking-wider text-amber-600">
              Human-in-the-Loop Approval Required
            </span>
            <h3 className="text-lg font-bold text-slate-900">
              Allow Safe Web Search?
            </h3>
          </div>
        </div>

        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
          The term <strong>&ldquo;{data.query}&rdquo;</strong> was not found in the official Stanford HAI glossary.
          DecodeAI can safely search educational sources using strict school-safe filters, or explain using general AI knowledge.
        </p>

        {/* Query inspection / editing */}
        <div className="mb-5">
          <label className="text-xs font-bold text-slate-700 block mb-1.5">
            Search Query Preview (editable):
          </label>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={currentQuery}
              onChange={(e) => setEditedQuery(e.target.value)}
              className="w-full clay-input pl-9 pr-3 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 bg-slate-50"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <button
            type="button"
            onClick={() => onDecision(data.request_id, "reject")}
            className="w-full sm:w-auto clay-btn px-4 py-2.5 bg-slate-100 text-slate-700 hover:text-slate-900 text-xs font-bold flex items-center justify-center gap-1.5"
          >
            <X className="w-4 h-4 text-rose-500" />
            Use AI Knowledge Only
          </button>

          <button
            type="button"
            onClick={() => onDecision(data.request_id, "approve", currentQuery)}
            className="w-full sm:w-auto clay-btn clay-btn-primary px-5 py-2.5 text-xs font-bold flex items-center justify-center gap-1.5"
          >
            <Check className="w-4 h-4" />
            Approve Safe Search
          </button>
        </div>
      </div>
    </div>
  );
}
