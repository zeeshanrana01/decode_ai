export interface TermExplanation {
  term: string;
  simple: string;
  mental_model: string;
  steps: string[];
  example: string;
  quiz: string;
  from_glossary: boolean;
  used_web_search: boolean;
}

export interface BadgeItem {
  badge_key: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
}

export interface DailyGoal {
  date: string;
  terms_count: number;
  target_terms: number;
  quizzes_count: number;
  target_quizzes: number;
  completed: boolean;
  bonus_collected: boolean;
}

export interface UserStats {
  id: string;
  name: string;
  xp: number;
  level: number;
  level_title: string;
  xp_in_level: number;
  xp_for_next_level: number;
  progress_percent: number;
  streak_count: number;
  streak_freezes: number;
  credits: number;
  daily_goal: DailyGoal;
  badges: BadgeItem[];
}

export interface QuizGradeResult {
  score: number; // 0 to 3
  feedback: string;
  xp_awarded: number;
  badge_unlocked?: string | null;
  streak_bonus: boolean;
  new_level?: number | null;
}

export interface GlossaryTerm {
  term: string;
  key: string;
  definition: string;
}

export interface HistoryItem {
  id: number;
  term: string;
  simple: string;
  mental_model: string;
  steps: string[];
  example: string;
  quiz: string;
  from_glossary: boolean;
  used_web_search: boolean;
  created_at: string;
}

export interface QuizHistoryRecord {
  id: number;
  term: string;
  question: string;
  user_answer: string;
  score: number;
  feedback: string;
  xp_awarded: number;
  created_at: string;
}

export interface HitlPromptData {
  request_id: string;
  tool: string;
  query: string;
  message: string;
}
