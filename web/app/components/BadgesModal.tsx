"use client";

import React from "react";
import { X, Award, CheckCircle2, Lock } from "lucide-react";
import { BadgeItem } from "../lib/types";

interface BadgesModalProps {
  isOpen: boolean;
  onClose: () => void;
  badges: BadgeItem[];
}

export default function BadgesModal({ isOpen, onClose, badges }: BadgesModalProps) {
  if (!isOpen) return null;

  const unlockedCount = badges.filter((b) => b.unlocked).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="clay-card p-6 sm:p-8 max-w-2xl w-full bg-white relative max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Badges & Achievements
              </h3>
              <p className="text-xs text-slate-500">
                Unlocked {unlockedCount} of {badges.length} student milestones
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

        {/* Badges Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 overflow-y-auto py-4 pr-1">
          {badges.map((badge) => (
            <div
              key={badge.badge_key}
              className={`p-4 rounded-2xl flex items-start gap-3 transition ${
                badge.unlocked ? "clay-badge-unlocked" : "clay-badge-locked"
              }`}
            >
              <div
                className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shrink-0 shadow-sm ${
                  badge.unlocked ? "bg-indigo-50 border border-indigo-200" : "bg-slate-200 grayscale"
                }`}
              >
                {badge.icon}
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-slate-800">
                    {badge.name}
                  </h4>
                  {badge.unlocked ? (
                    <span className="text-[10px] font-bold text-emerald-600 flex items-center gap-0.5">
                      <CheckCircle2 className="w-3 h-3" /> Unlocked
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold text-slate-400 flex items-center gap-0.5">
                      <Lock className="w-3 h-3" /> Locked
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                  {badge.description}
                </p>
                {badge.unlocked_at && (
                  <span className="text-[10px] text-indigo-400 block mt-1 font-medium">
                    Unlocked: {new Date(badge.unlocked_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
