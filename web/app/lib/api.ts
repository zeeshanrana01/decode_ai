import {
  UserStats,
  GlossaryTerm,
  QuizGradeResult,
  HistoryItem,
  QuizHistoryRecord,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchUserStats(userId = "student_1"): Promise<UserStats> {
  const res = await fetch(`${API_BASE}/api/user/stats?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to load user stats");
  return res.json();
}

export async function fetchGlossary(): Promise<{ total: number; terms: GlossaryTerm[] }> {
  const res = await fetch(`${API_BASE}/api/glossary`);
  if (!res.ok) throw new Error("Failed to load glossary");
  return res.json();
}

export async function submitQuizAnswer(
  term: string,
  quiz: string,
  userAnswer: string,
  userId = "student_1"
): Promise<QuizGradeResult> {
  const res = await fetch(`${API_BASE}/api/quiz/grade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      term,
      quiz,
      user_answer: userAnswer,
      user_id: userId,
    }),
  });
  if (!res.ok) throw new Error("Failed to grade quiz");
  return res.json();
}

export async function submitHitlDecision(
  requestId: string,
  decision: "approve" | "reject",
  editedQuery?: string,
  userId = "student_1"
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/hitl/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_id: requestId,
      decision,
      user_id: userId,
      edited_query: editedQuery,
    }),
  });
  if (!res.ok) throw new Error("Failed to submit HITL decision");
  return res.json();
}

export async function buyStreakFreeze(userId = "student_1"): Promise<any> {
  const res = await fetch(`${API_BASE}/api/user/freeze/buy?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to buy streak freeze");
  }
  return res.json();
}

export async function fetchHistory(
  userId = "student_1"
): Promise<{ history: HistoryItem[]; quizzes: QuizHistoryRecord[] }> {
  const res = await fetch(`${API_BASE}/api/history?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to load history");
  return res.json();
}

export function getStreamUrl(term: string, allowWebSearch: boolean, userId = "student_1"): string {
  const encodedTerm = encodeURIComponent(term);
  return `${API_BASE}/api/explain/stream?term=${encodedTerm}&user_id=${userId}&allow_web_search=${allowWebSearch}`;
}
