"use client";

import React, { useState, useEffect } from "react";
import { X, History, Star, Clock, BookOpen, Sparkles } from "lucide-react";
import { fetchHistory } from "../lib/api";
import { HistoryItem, QuizHistoryRecord } from "../lib/types";

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  onSelectTerm: (term: string) => void;
}

export default function HistoryModal({
  isOpen,
  onClose,
  userId,
  onSelectTerm,
}: HistoryModalProps) {
  const [activeTab, setActiveTab] = useState<"terms" | "quizzes">("terms");
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [quizzes, setQuizzes] = useState<QuizHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen, userId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchHistory(userId);
      setHistoryItems(data.history || []);
      setQuizzes(data.quizzes || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="clay-card p-6 sm:p-8 max-w-2xl w-full bg-white relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Learning History
              </h3>
              <p className="text-xs text-slate-500">
                Review your past AI term explorations and quizzes
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

        {/* Tabs */}
        <div className="flex items-center gap-2 my-4">
          <button
            onClick={() => setActiveTab("terms")}
            className={`clay-pill px-4 py-1.5 text-xs font-bold transition ${
              activeTab === "terms"
                ? "bg-indigo-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Explored Terms ({historyItems.length})
          </button>
          <button
            onClick={() => setActiveTab("quizzes")}
            className={`clay-pill px-4 py-1.5 text-xs font-bold transition ${
              activeTab === "quizzes"
                ? "bg-indigo-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Quiz Submissions ({quizzes.length})
          </button>
        </div>

        {/* Content list */}
        <div className="overflow-y-auto flex-1 pr-1 space-y-3">
          {loading ? (
            <div className="py-12 text-center text-xs font-bold text-slate-400">
              Loading history...
            </div>
          ) : activeTab === "terms" ? (
            historyItems.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400">
                No terms explored yet. Try searching for a concept!
              </div>
            ) : (
              historyItems.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-indigo-200 transition group flex flex-col gap-1.5 cursor-pointer"
                  onClick={() => {
                    onSelectTerm(item.term);
                    onClose();
                  }}
                >
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-slate-800 group-hover:text-indigo-600">
                      {item.term}
                    </h4>
                    <span className="text-[10px] text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-2">
                    {item.simple}
                  </p>
                  <div className="text-[11px] text-indigo-500 font-semibold italic line-clamp-1">
                    &ldquo;{item.mental_model}&rdquo;
                  </div>
                </div>
              ))
            )
          ) : quizzes.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              No quizzes completed yet. Answer a quiz to earn stars!
            </div>
          ) : (
            quizzes.map((q) => (
              <div
                key={q.id}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">
                    Term: {q.term}
                  </span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3].map((s) => (
                      <Star
                        key={s}
                        className={`w-3.5 h-3.5 ${
                          s <= q.score ? "text-amber-400 fill-amber-400" : "text-slate-200 fill-slate-200"
                        }`}
                      />
                    ))}
                    <span className="text-xs font-black ml-1 text-slate-700">
                      {q.score}/3
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-600 bg-white p-2.5 rounded-xl border border-slate-100">
                  <span className="font-bold text-slate-500 block mb-0.5">Your Answer:</span>
                  &ldquo;{q.user_answer}&rdquo;
                </div>

                <p className="text-xs text-slate-700 font-medium">
                  <strong>Feedback:</strong> {q.feedback}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
