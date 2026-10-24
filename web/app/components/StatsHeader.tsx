"use client";

import React, { useState } from "react";
import { UserStats } from "../lib/types";
import { buyStreakFreeze } from "../lib/api";
import { Sparkles, Flame, Snowflake, Zap, Award, History, BookOpen, PlusCircle } from "lucide-react";

interface StatsHeaderProps {
  stats: UserStats | null;
  onOpenBadges: () => void;
  onOpenHistory: () => void;
  onOpenGlossary: () => void;
  onRefreshStats: () => void;
}

export default function StatsHeader({
  stats,
  onOpenBadges,
  onOpenHistory,
  onOpenGlossary,
  onRefreshStats,
}: StatsHeaderProps) {
  const [buyingFreeze, setBuyingFreeze] = useState(false);
  const [freezeMsg, setFreezeMsg] = useState<string | null>(null);

  if (!stats) return null;

  const handleBuyFreeze = async () => {
    try {
      setBuyingFreeze(true);
      const res = await buyStreakFreeze(stats.id);
      setFreezeMsg(res.message);
      onRefreshStats();
      setTimeout(() => setFreezeMsg(null), 3000);
    } catch (e: any) {
      alert(e.message || "Could not buy streak freeze");
    } finally {
      setBuyingFreeze(false);
    }
  };

  const unlockedCount = stats.badges.filter((b) => b.unlocked).length;

  return (
    <header className="w-full max-w-5xl mx-auto mb-6 px-4 pt-4">
      <div className="clay-card p-4 sm:p-6 bg-white/90 backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4">
        {/* App Title & Level Info */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg shadow-indigo-200">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-slate-800 tracking-tight">
                Decode<span className="text-indigo-600">AI</span>
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-indigo-100 text-indigo-700">
                School Edition
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mt-0.5">
              <span>Lvl {stats.level}: <strong className="text-indigo-600">{stats.level_title}</strong></span>
              <span>•</span>
              <span>{stats.xp} XP</span>
            </div>
          </div>
        </div>

        {/* Level XP Progress Bar */}
        <div className="w-full md:w-48 flex flex-col gap-1">
          <div className="flex justify-between text-xs font-bold text-slate-600">
            <span>XP Progress</span>
            <span>{stats.progress_percent}%</span>
          </div>
          <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden p-0.5 shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(stats.progress_percent, 100)}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-400 text-right">
            Next Level at {stats.xp_for_next_level} XP
          </span>
        </div>

        {/* Gamification Stats: Streak, Freezes, Credits */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          {/* Streak Flame */}
          <div
            className="clay-pill px-3 py-1.5 bg-amber-50 text-amber-800 flex items-center gap-1.5 text-xs font-bold"
            title={`${stats.streak_count} day learning streak!`}
          >
            <Flame className="w-4 h-4 text-amber-500 fill-amber-500 animate-bounce" />
            <span>{stats.streak_count} {stats.streak_count === 1 ? "day" : "days"}</span>
          </div>

          {/* Streak Freeze */}
          <div
            className="clay-pill px-3 py-1.5 bg-sky-50 text-sky-800 flex items-center gap-1.5 text-xs font-bold"
            title={`${stats.streak_freezes} Streak Freezes available`}
          >
            <Snowflake className="w-4 h-4 text-sky-500" />
            <span>{stats.streak_freezes}</span>
            <button
              onClick={handleBuyFreeze}
              disabled={buyingFreeze || stats.credits < 5}
              className="text-sky-600 hover:text-sky-800 disabled:opacity-30 transition ml-0.5"
              title="Get an extra freeze (costs 5 credits)"
            >
              <PlusCircle className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Energy Credits */}
          <div
            className="clay-pill px-3 py-1.5 bg-emerald-50 text-emerald-800 flex items-center gap-1.5 text-xs font-bold"
            title={`${stats.credits} daily energy credits remaining`}
          >
            <Zap className="w-4 h-4 text-emerald-500 fill-emerald-500" />
            <span>{stats.credits} / 20</span>
          </div>
        </div>

        {/* Modal Triggers: Badges, History, Glossary */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenBadges}
            className="clay-btn px-3 py-1.5 bg-white text-slate-700 hover:text-indigo-600 text-xs flex items-center gap-1.5"
            title="View Badges & Achievements"
          >
            <Award className="w-4 h-4 text-purple-500" />
            <span className="hidden sm:inline">Badges</span>
            <span className="bg-purple-100 text-purple-700 font-bold px-1.5 py-0.2 rounded-full text-[10px]">
              {unlockedCount}/7
            </span>
          </button>

          <button
            onClick={onOpenHistory}
            className="clay-btn px-3 py-1.5 bg-white text-slate-700 hover:text-indigo-600 text-xs flex items-center gap-1.5"
            title="View Explanations & Quiz History"
          >
            <History className="w-4 h-4 text-indigo-500" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={onOpenGlossary}
            className="clay-btn px-3 py-1.5 bg-white text-slate-700 hover:text-indigo-600 text-xs flex items-center gap-1.5"
            title="Browse all 109 Glossary Terms"
          >
            <BookOpen className="w-4 h-4 text-emerald-500" />
            <span className="hidden sm:inline">Glossary</span>
          </button>
        </div>
      </div>

      {freezeMsg && (
        <div className="mt-2 p-2 text-center text-xs font-bold text-sky-800 bg-sky-100 rounded-xl animate-fade-in shadow">
          {freezeMsg}
        </div>
      )}
    </header>
  );
}
