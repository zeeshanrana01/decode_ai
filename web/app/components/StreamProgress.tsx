"use client";

import React from "react";
import { ShieldCheck, BookOpen, Globe, Lightbulb, HelpCircle, Check, Loader2 } from "lucide-react";

interface StreamStep {
  id: string;
  label: string;
  detail: string;
  status: "pending" | "active" | "completed";
  icon: React.ReactNode;
}

interface StreamProgressProps {
  steps: StreamStep[];
  currentThought: string | null;
}

export default function StreamProgress({ steps, currentThought }: StreamProgressProps) {
  if (steps.length === 0) return null;

  return (
    <div className="w-full max-w-4xl mx-auto px-4 mb-8">
      <div className="clay-card p-5 sm:p-6 bg-white/90 backdrop-blur-md pulse-glow">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
            </span>
            <h3 className="text-sm font-bold text-slate-800">
              DecodeAI Agent Reasoning Stream
            </h3>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
            Live SSE
          </span>
        </div>

        {/* Steps Tracker */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {steps.map((s) => (
            <div
              key={s.id}
              className={`p-3 rounded-2xl flex items-center gap-3 transition-all ${
                s.status === "completed"
                  ? "bg-emerald-50 border border-emerald-200 text-emerald-900"
                  : s.status === "active"
                  ? "bg-indigo-50 border-2 border-indigo-400 text-indigo-900 shadow-md"
                  : "bg-slate-50 border border-slate-100 text-slate-400 opacity-60"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  s.status === "completed"
                    ? "bg-emerald-500 text-white"
                    : s.status === "active"
                    ? "bg-indigo-600 text-white animate-pulse"
                    : "bg-slate-200 text-slate-500"
                }`}
              >
                {s.status === "completed" ? (
                  <Check className="w-4 h-4 stroke-[3]" />
                ) : s.status === "active" ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  s.icon
                )}
              </div>

              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate">{s.label}</div>
                <div className="text-[10px] truncate opacity-75">{s.detail}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Thought bubble */}
        {currentThought && (
          <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-start gap-2.5">
            <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
              <Lightbulb className="w-3.5 h-3.5" />
            </div>
            <div className="text-xs text-slate-700 font-medium italic">
              &ldquo;{currentThought}&rdquo;
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
