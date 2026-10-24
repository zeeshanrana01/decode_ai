"use client";

import React, { useState, useEffect } from "react";
import {
  fetchUserStats,
  fetchGlossary,
  submitHitlDecision,
  getStreamUrl,
} from "./lib/api";
import {
  UserStats,
  GlossaryTerm,
  TermExplanation,
  HitlPromptData,
  QuizGradeResult,
} from "./lib/types";
import StatsHeader from "./components/StatsHeader";
import DailyGoalTracker from "./components/DailyGoalTracker";
import SearchBar from "./components/SearchBar";
import StreamProgress from "./components/StreamProgress";
import TermCard from "./components/TermCard";
import HitlModal from "./components/HitlModal";
import BadgesModal from "./components/BadgesModal";
import HistoryModal from "./components/HistoryModal";
import GlossaryModal from "./components/GlossaryModal";
import { Sparkles, Shield, Trophy, Lightbulb, AlertCircle } from "lucide-react";

export default function Home() {
  const [userId] = useState("student_1");
  const [stats, setStats] = useState<UserStats | null>(null);
  const [glossaryTerms, setGlossaryTerms] = useState<GlossaryTerm[]>([]);
  const [explanation, setExplanation] = useState<TermExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [streamSteps, setStreamSteps] = useState<any[]>([]);
  const [currentThought, setCurrentThought] = useState<string | null>(null);
  const [hitlData, setHitlData] = useState<HitlPromptData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modals
  const [showBadges, setShowBadges] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showGlossary, setShowGlossary] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, [userId]);

  const loadInitialData = async () => {
    try {
      const [uStats, gData] = await Promise.all([
        fetchUserStats(userId).catch(() => null),
        fetchGlossary().catch(() => ({ total: 0, terms: [] })),
      ]);
      if (uStats) setStats(uStats);
      if (gData.terms) setGlossaryTerms(gData.terms);
    } catch (e) {
      console.error("Initialization error:", e);
    }
  };

  const handleSearch = (term: string, allowWebSearch: boolean) => {
    setErrorMessage(null);
    setIsLoading(true);
    setExplanation(null);
    setCurrentThought("Starting reasoning pipeline...");

    const initialSteps = [
      { id: "guardrails", label: "Guardrails", detail: "Safety & Privacy Check", status: "active", icon: <Shield className="w-4 h-4" /> },
      { id: "lookup", label: "Glossary", detail: "Stanford HAI Lookup", status: "pending", icon: <Lightbulb className="w-4 h-4" /> },
      { id: "synthesis", label: "3 Steps", detail: "Analogy & Steps", status: "pending", icon: <Sparkles className="w-4 h-4" /> },
      { id: "quiz", label: "Quiz", detail: "Interactive Test", status: "pending", icon: <Trophy className="w-4 h-4" /> },
    ];
    setStreamSteps(initialSteps);

    const streamUrl = getStreamUrl(term, allowWebSearch, userId);
    const eventSource = new EventSource(streamUrl);

    eventSource.addEventListener("status", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        setCurrentThought(data.message);

        setStreamSteps((prev) =>
          prev.map((s) => {
            if (data.step === "guardrails_passed" && s.id === "guardrails") {
              return { ...s, status: "completed" };
            }
            if (data.step === "glossary_lookup" && s.id === "lookup") {
              return { ...s, status: "active" };
            }
            if (data.step === "synthesizing" && s.id === "synthesis") {
              return { ...s, status: "active" };
            }
            return s;
          })
        );
      } catch (err) {
        console.error("Parse status error:", err);
      }
    });

    eventSource.addEventListener("thought", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        setCurrentThought(data.message);

        if (data.step === "glossary_found") {
          setStreamSteps((prev) =>
            prev.map((s) => (s.id === "lookup" ? { ...s, status: "completed" } : s))
          );
        }
      } catch (err) {
        console.error("Parse thought error:", err);
      }
    });

    eventSource.addEventListener("hitl_prompt", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        setHitlData(data);
      } catch (err) {
        console.error("Parse hitl error:", err);
      }
    });

    eventSource.addEventListener("explanation", (e: any) => {
      try {
        const data: TermExplanation = JSON.parse(e.data);
        setExplanation(data);
        setStreamSteps((prev) =>
          prev.map((s) => ({ ...s, status: "completed" }))
        );
      } catch (err) {
        console.error("Parse explanation error:", err);
      }
    });

    eventSource.addEventListener("gamification", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        if (data.stats) {
          setStats(data.stats);
        }
      } catch (err) {
        console.error("Parse gamification error:", err);
      }
    });

    eventSource.addEventListener("error", (e: any) => {
      try {
        if (e.data) {
          const err = JSON.parse(e.data);
          setErrorMessage(err.message || "An unexpected error occurred.");
        }
      } catch {
        // Network or stream close
      }
      setIsLoading(false);
      eventSource.close();
    });

    eventSource.addEventListener("done", () => {
      setIsLoading(false);
      eventSource.close();
    });

    eventSource.onerror = () => {
      setIsLoading(false);
      eventSource.close();
    };
  };

  const handleHitlDecision = async (
    requestId: string,
    decision: "approve" | "reject",
    editedQuery?: string
  ) => {
    try {
      await submitHitlDecision(requestId, decision, editedQuery, userId);
      const queryToRun = editedQuery || (hitlData ? hitlData.query : "");
      setHitlData(null);
      if (queryToRun) {
        handleSearch(queryToRun, decision === "approve");
      }
    } catch (e: any) {
      alert(e.message || "Failed to submit HITL decision");
    }
  };

  const handleGradeReceived = (result: QuizGradeResult) => {
    loadInitialData();
  };

  return (
    <div className="min-h-screen pb-16 flex flex-col justify-between">
      <div>
        {/* Top Gamification Header */}
        <StatsHeader
          stats={stats}
          onOpenBadges={() => setShowBadges(true)}
          onOpenHistory={() => setShowHistory(true)}
          onOpenGlossary={() => setShowGlossary(true)}
          onRefreshStats={loadInitialData}
        />

        {/* Daily Goal Bar */}
        <DailyGoalTracker goal={stats ? stats.daily_goal : null} />

        {/* Main Search Bar */}
        <SearchBar
          onSearch={(term, allowWeb) => handleSearch(term, allowWeb)}
          isLoading={isLoading}
          glossaryTerms={glossaryTerms}
        />

        {/* Error / Guardrail Alert */}
        {errorMessage && (
          <div className="w-full max-w-4xl mx-auto px-4 mb-6">
            <div className="clay-card p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <div className="text-xs sm:text-sm font-bold">{errorMessage}</div>
            </div>
          </div>
        )}

        {/* Live SSE Streaming Progress */}
        {isLoading && (
          <StreamProgress
            steps={streamSteps}
            currentThought={currentThought}
          />
        )}

        {/* Term Explanation Card */}
        {explanation && !isLoading && (
          <TermCard
            explanation={explanation}
            userId={userId}
            onGradeReceived={handleGradeReceived}
          />
        )}

        {/* Hero Section if nothing is searched yet */}
        {!explanation && !isLoading && (
          <main className="w-full max-w-4xl mx-auto px-4 py-8">
            <div className="clay-card p-8 sm:p-12 text-center bg-white/80 backdrop-blur-sm">
              <div className="w-16 h-16 rounded-3xl bg-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-inner">
                <Sparkles className="w-8 h-8 animate-pulse" />
              </div>
              <h2 className="text-2xl sm:text-4xl font-black text-slate-800 tracking-tight mb-3">
                Decode Any AI Term in Seconds
              </h2>
              <p className="max-w-xl mx-auto text-sm sm:text-base text-slate-500 font-medium leading-relaxed mb-8">
                Designed specifically for middle and high school students. Get clear, everyday mental models, 3 action steps, real-life examples, and instant 0–3 star quizzes!
              </p>

              {/* Feature Highlights Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                <div className="clay-card-lavender p-5 rounded-2xl">
                  <div className="text-2xl mb-2">🧠</div>
                  <h3 className="text-sm font-bold text-slate-800 mb-1">
                    Mental Models + 3 Steps
                  </h3>
                  <p className="text-xs text-slate-600">
                    No confusing jargon. Understand through everyday analogies like school lockers, kitchen cooking, or video games.
                  </p>
                </div>

                <div className="clay-card-mint p-5 rounded-2xl">
                  <div className="text-2xl mb-2">🎮</div>
                  <h3 className="text-sm font-bold text-slate-800 mb-1">
                    Gamified Learning
                  </h3>
                  <p className="text-xs text-slate-600">
                    Earn XP, advance levels, build streaks, unlock badges, and protect your streak with frost freeze!
                  </p>
                </div>

                <div className="clay-card-peach p-5 rounded-2xl">
                  <div className="text-2xl mb-2">🛡️</div>
                  <h3 className="text-sm font-bold text-slate-800 mb-1">
                    School-Safe Guardrails
                  </h3>
                  <p className="text-xs text-slate-600">
                    Strict content filters, PII redaction, prompt injection defense, and Human-in-the-Loop web search approval.
                  </p>
                </div>
              </div>
            </div>
          </main>
        )}
      </div>

      {/* Footer */}
      <footer className="w-full text-center py-6 text-xs text-slate-400 font-medium">
        DecodeAI • Built for students with FastAPI + LangChain + SQLModel & Next.js Claymorphism
      </footer>

      {/* Modals */}
      <HitlModal
        data={hitlData}
        onDecision={handleHitlDecision}
        onClose={() => setHitlData(null)}
      />

      <BadgesModal
        isOpen={showBadges}
        onClose={() => setShowBadges(false)}
        badges={stats ? stats.badges : []}
      />

      <HistoryModal
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        userId={userId}
        onSelectTerm={(term) => handleSearch(term, false)}
      />

      <GlossaryModal
        isOpen={showGlossary}
        onClose={() => setShowGlossary(false)}
        terms={glossaryTerms}
        onSelectTerm={(term) => handleSearch(term, false)}
      />
    </div>
  );
}
