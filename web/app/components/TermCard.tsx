"use client";

import React from "react";
import { BookOpen, Sparkles, Globe, Lightbulb, Compass, Share2 } from "lucide-react";
import { TermExplanation, QuizGradeResult } from "../lib/types";
import MentalModelSteps from "./MentalModelSteps";
import QuizCard from "./QuizCard";

interface TermCardProps {
  explanation: TermExplanation;
  userId: string;
  onGradeReceived: (result: QuizGradeResult) => void;
}

export default function TermCard({
  explanation,
  userId,
  onGradeReceived,
}: TermCardProps) {
  return (
    <article className="w-full max-w-4xl mx-auto px-4 mb-12">
      <div className="clay-card p-6 sm:p-8 bg-white/95 backdrop-blur-sm transition-all duration-300">
        {/* Header: Term Title & Badges */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-5 border-b border-slate-100">
          <div>
            <span className="text-xs font-black uppercase tracking-wider text-indigo-500">
              AI Term Explained
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-0.5">
              {explanation.term}
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {explanation.from_glossary ? (
              <span className="clay-pill px-3 py-1 bg-emerald-50 text-emerald-800 text-xs font-bold flex items-center gap-1.5 border border-emerald-200">
                <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
                Stanford HAI Glossary
              </span>
            ) : explanation.used_web_search ? (
              <span className="clay-pill px-3 py-1 bg-sky-50 text-sky-800 text-xs font-bold flex items-center gap-1.5 border border-sky-200">
                <Globe className="w-3.5 h-3.5 text-sky-600" />
                Safe Web Search
              </span>
            ) : (
              <span className="clay-pill px-3 py-1 bg-purple-50 text-purple-800 text-xs font-bold flex items-center gap-1.5 border border-purple-200">
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                AI Knowledge Base
              </span>
            )}
          </div>
        </div>

        {/* Section 1: Simple Explanation */}
        <div className="mt-6 mb-6">
          <div className="clay-card-lavender p-5 rounded-2xl">
            <span className="text-[11px] font-black uppercase tracking-wider text-indigo-700 block mb-1">
              In Plain English
            </span>
            <p className="text-base sm:text-lg font-bold text-slate-900 leading-relaxed">
              {explanation.simple}
            </p>
          </div>
        </div>

        {/* Section 2: Mental Model & Analogy */}
        <div className="mb-6">
          <div className="clay-card-peach p-5 rounded-2xl mb-4">
            <div className="flex items-center gap-2 mb-1.5">
              <Lightbulb className="w-4 h-4 text-orange-600" />
              <span className="text-[11px] font-black uppercase tracking-wider text-orange-800">
                Mental Model Analogy
              </span>
            </div>
            <p className="text-sm sm:text-base font-extrabold text-slate-800 leading-relaxed">
              &ldquo;{explanation.mental_model}&rdquo;
            </p>
          </div>

          {/* 3 Steps Breakdown */}
          <MentalModelSteps steps={explanation.steps} />
        </div>

        {/* Section 3: Real-Life Example */}
        <div className="mb-6">
          <div className="clay-card-sky p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-1.5">
              <Compass className="w-4 h-4 text-sky-600" />
              <span className="text-[11px] font-black uppercase tracking-wider text-sky-800">
                Real-Life School / Everyday Example
              </span>
            </div>
            <p className="text-xs sm:text-sm font-semibold text-slate-800 leading-relaxed">
              {explanation.example}
            </p>
          </div>
        </div>

        {/* Section 4: Interactive Quiz */}
        <QuizCard
          term={explanation.term}
          quizQuestion={explanation.quiz}
          userId={userId}
          onGradeReceived={onGradeReceived}
        />
      </div>
    </article>
  );
}
