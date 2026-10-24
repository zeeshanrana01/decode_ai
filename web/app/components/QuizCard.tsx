"use client";

import React, { useState } from "react";
import confetti from "canvas-confetti";
import { HelpCircle, Send, Star, Trophy, Sparkles, CheckCircle, RefreshCw } from "lucide-react";
import { submitQuizAnswer } from "../lib/api";
import { QuizGradeResult } from "../lib/types";

interface QuizCardProps {
  term: string;
  quizQuestion: string;
  userId: string;
  onGradeReceived: (result: QuizGradeResult) => void;
}

export default function QuizCard({
  term,
  quizQuestion,
  userId,
  onGradeReceived,
}: QuizCardProps) {
  const [answer, setAnswer] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [gradeResult, setGradeResult] = useState<QuizGradeResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || isSubmitting) return;

    try {
      setIsSubmitting(true);
      const res = await submitQuizAnswer(term, quizQuestion, answer.trim(), userId);
      setGradeResult(res);
      onGradeReceived(res);

      // Trigger confetti on score 3 (mastery!)
      if (res.score === 3) {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
    } catch (e: any) {
      alert(e.message || "Failed to grade quiz");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getScoreBadge = (score: number) => {
    switch (score) {
      case 3:
        return {
          title: "Mastery!",
          bg: "bg-emerald-100 text-emerald-800 border-emerald-300",
          stars: 3,
        };
      case 2:
        return {
          title: "Great Job!",
          bg: "bg-indigo-100 text-indigo-800 border-indigo-300",
          stars: 2,
        };
      case 1:
        return {
          title: "Good Start!",
          bg: "bg-amber-100 text-amber-800 border-amber-300",
          stars: 1,
        };
      default:
        return {
          title: "Keep Practicing!",
          bg: "bg-rose-100 text-rose-800 border-rose-300",
          stars: 0,
        };
    }
  };

  return (
    <div className="mt-6 pt-6 border-t border-slate-100">
      <div className="clay-card-amber p-5 sm:p-6 rounded-3xl">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-md shadow-amber-200">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm sm:text-base font-extrabold text-slate-800">
                Quick Check Quiz: Test Your Understanding
              </h4>
              <p className="text-xs text-slate-500">
                Answer in your own words or choose the correct option (Grades 0–3 Stars)
              </p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full font-bold bg-amber-200/80 text-amber-900 shrink-0">
            Earn up to +50 XP
          </span>
        </div>

        {/* Question Box */}
        <div className="clay-input p-4 bg-white/90 mb-4">
          <p className="text-sm sm:text-base font-bold text-slate-800 leading-relaxed">
            {quizQuestion}
          </p>
        </div>

        {/* Answer Form */}
        {!gradeResult ? (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              disabled={isSubmitting}
              className="flex-1 clay-input px-4 py-3 text-sm font-medium text-slate-800 bg-white"
            />
            <button
              type="submit"
              disabled={isSubmitting || !answer.trim()}
              className="clay-btn clay-btn-primary px-6 py-3 text-sm font-bold disabled:opacity-50 flex items-center justify-center gap-2 shrink-0"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Grading...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Check Answer
                </>
              )}
            </button>
          </form>
        ) : (
          /* Grade & Feedback Display */
          <div className="clay-card p-5 bg-white space-y-4 animate-fade-in">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
              {/* Star rating */}
              <div className="flex items-center gap-1.5">
                {[1, 2, 3].map((starIdx) => (
                  <Star
                    key={starIdx}
                    className={`w-6 h-6 ${
                      starIdx <= gradeResult.score
                        ? "text-amber-400 fill-amber-400 drop-shadow"
                        : "text-slate-200 fill-slate-100"
                    }`}
                  />
                ))}
                <span
                  className={`ml-2 px-3 py-1 rounded-full text-xs font-black border ${
                    getScoreBadge(gradeResult.score).bg
                  }`}
                >
                  Score: {gradeResult.score} / 3 • {getScoreBadge(gradeResult.score).title}
                </span>
              </div>

              {/* XP Awarded badge */}
              <div className="flex items-center gap-1.5 text-xs font-black px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700">
                <Sparkles className="w-4 h-4 text-indigo-500" />
                <span>+{gradeResult.xp_awarded} XP Earned!</span>
              </div>
            </div>

            {/* Teacher Feedback */}
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                Teacher's Feedback
              </div>
              <p className="text-sm font-semibold text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-2xl border border-slate-100">
                {gradeResult.feedback}
              </p>
            </div>

            {/* Unlocked badge alert if any */}
            {gradeResult.badge_unlocked && (
              <div className="p-3 bg-purple-50 border border-purple-200 rounded-2xl flex items-center gap-3 text-purple-900">
                <Trophy className="w-6 h-6 text-purple-600 animate-bounce" />
                <div className="text-xs">
                  <span className="font-extrabold block">New Badge Unlocked!</span>
                  <span>You earned: <strong>{gradeResult.badge_unlocked}</strong></span>
                </div>
              </div>
            )}

            {/* Try again option */}
            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => {
                  setGradeResult(null);
                  setAnswer("");
                }}
                className="clay-btn px-4 py-2 bg-slate-100 text-slate-700 hover:text-slate-900 text-xs font-bold"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
