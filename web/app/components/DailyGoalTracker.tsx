"use client";

import React from "react";
import { DailyGoal } from "../lib/types";
import { Target, CheckCircle2, Trophy } from "lucide-react";

interface DailyGoalTrackerProps {
  goal: DailyGoal | null;
}

export default function DailyGoalTracker({ goal }: DailyGoalTrackerProps) {
  if (!goal) return null;

  const termsPercent = Math.min(Math.round((goal.terms_count / goal.target_terms) * 100), 100);
  const quizzesPercent = Math.min(Math.round((goal.quizzes_count / goal.target_quizzes) * 100), 100);

  return (
    <div className="w-full max-w-5xl mx-auto px-4 mb-6">
      <div className={`clay-card p-4 sm:p-5 transition-all ${goal.completed ? "bg-amber-50/90 border-amber-200" : "bg-white/80"}`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${goal.completed ? "bg-amber-500 text-white shadow-md shadow-amber-200" : "bg-indigo-100 text-indigo-600"}`}>
              {goal.completed ? <Trophy className="w-5 h-5 animate-bounce" /> : <Target className="w-5 h-5" />}
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                Today's Learning Goal
                {goal.completed && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-amber-200 text-amber-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-amber-700" /> +50 XP Bonus Claimed!
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-500">
                {goal.completed ? "Awesome job! You reached today's target." : "Complete these activities to earn 50 bonus XP today!"}
              </p>
            </div>
          </div>

          <div className="text-xs font-semibold text-slate-400">
            Date: {goal.date}
          </div>
        </div>

        {/* Progress Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Terms Target */}
          <div className="clay-input p-3 bg-white/70">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-1.5">
              <span>Explain AI Terms</span>
              <span className={goal.terms_count >= goal.target_terms ? "text-emerald-600 font-extrabold" : "text-slate-500"}>
                {goal.terms_count} / {goal.target_terms}
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-300"
                style={{ width: `${termsPercent}%` }}
              />
            </div>
          </div>

          {/* Quizzes Target */}
          <div className="clay-input p-3 bg-white/70">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-1.5">
              <span>Complete AI Quizzes</span>
              <span className={goal.quizzes_count >= goal.target_quizzes ? "text-emerald-600 font-extrabold" : "text-slate-500"}>
                {goal.quizzes_count} / {goal.target_quizzes}
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-300"
                style={{ width: `${quizzesPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
