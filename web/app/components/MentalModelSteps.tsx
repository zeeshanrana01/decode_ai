"use client";

import React from "react";
import { ArrowRight, Layers, Cpu, CheckCircle } from "lucide-react";

interface MentalModelStepsProps {
  steps: string[];
}

export default function MentalModelSteps({ steps }: MentalModelStepsProps) {
  if (!steps || steps.length === 0) return null;

  const stepMeta = [
    { title: "Step 1: Input / Setup", bg: "clay-card-sky", accent: "bg-sky-500", textAccent: "text-sky-700" },
    { title: "Step 2: How It Works", bg: "clay-card-lavender", accent: "bg-indigo-500", textAccent: "text-indigo-700" },
    { title: "Step 3: The Result", bg: "clay-card-mint", accent: "bg-emerald-500", textAccent: "text-emerald-700" },
  ];

  return (
    <div className="mt-4">
      <div className="flex items-center gap-2 mb-3">
        <Layers className="w-4 h-4 text-indigo-600" />
        <h4 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-slate-700">
          3 Steps: How It Works in Action
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {steps.map((stepText, idx) => {
          const meta = stepMeta[idx] || stepMeta[0];
          // Strip "1. " or "Step 1: " prefix if present for clean card presentation
          const cleanText = stepText.replace(/^[0-9]+[.:]\s*/, "");

          return (
            <div
              key={idx}
              className={`p-4 rounded-2xl ${meta.bg} flex flex-col justify-between relative group hover:scale-[1.02] transition duration-200`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`w-7 h-7 rounded-full ${meta.accent} text-white font-black text-xs flex items-center justify-center shadow-md`}>
                    {idx + 1}
                  </span>
                  <span className={`text-[11px] font-bold ${meta.textAccent}`}>
                    {idx === 0 ? "Setup" : idx === 1 ? "Process" : "Outcome"}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-800 font-semibold leading-relaxed">
                  {cleanText}
                </p>
              </div>

              {idx < steps.length - 1 && (
                <div className="hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-white shadow-md text-slate-400 items-center justify-center">
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
