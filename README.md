# 🧠 DecodeAI — AI Term Explainer for School Students

**DecodeAI** is an interactive, gamified AI concept explainer tailored for middle and high school students (ages 11–18). It translates intimidating artificial intelligence jargon into memorable everyday mental models, 3-step action breakdowns, real-world school examples, and instant 0–3 star quizzes.

Built with a modern stack:
- **Backend (`api/`)**: FastAPI + LangChain `create_agent` + SQLModel (SQLite) + SSE streaming, run with `uv run fastapi dev`.
- **Frontend (`web/`)**: Next.js (App Router) + Tailwind CSS + Claymorphism 3D puffy UI with tactile animations.
- **Data (`data/`)**: Verified Stanford Institute for Human-Centered AI (HAI) Glossary containing 100+ AI terms.

---

## 📸 Key Features

### 1. 🤖 LangChain Agent Architecture
- **Official Tool 1 (`lookup_term`)**: Instant lookup across 109 terms from Stanford HAI glossary.
- **Official Tool 2 (`safe_web_search`)**: Strict school-safe educational search for terms outside the glossary.
- **Human-in-the-Loop (HITL)**: If a term is unknown and web search is proposed, the agent pauses and requests approval via a friendly modal before searching.
- **Structured Output**: Strictly typed via Pydantic:
  - `simple`: One clear sentence a beginner understands.
  - `mental_model`: An everyday analogy (kitchen, classroom, phone, video games).
  - `steps`: Exactly 3 sequential action steps explaining how the concept functions.
  - `example`: A real-life student scenario (e.g. Netflix recommendations, face filters).
  - `quiz`: A short question to test understanding.
  - `from_glossary`: Boolean indicating source authenticity.
- **SSE Streaming**: Real-time Server-Sent Events displaying reasoning steps (Guardrails verified → Glossary search → Analogy crafting → Quiz generation).

### 2. 🎯 Interactive 0–3 Star Quiz Grader
- Students type their answer to the generated quiz question.
- Evaluated on a **0 to 3 scale**:
  - `0`: Keep practicing (effort recognized)
  - `1`: Good start / partially correct
  - `2`: Great job / solid understanding
  - `3`: Full mastery! (Triggers confetti celebration 🎉)
- Provides encouraging, constructive teacher feedback.

### 3. 🎮 Gamification & Student Engagement
- **XP & Levels**: Earn XP for exploring terms (+20 XP), completing quizzes (+5 to +50 XP), and daily goals (+50 XP).
  - Level 1: *Curious Spark*
  - Level 2: *Prompt Explorer*
  - Level 3: *Neural Cadet*
  - Level 4: *Algorithm Knight*
  - Level 5: *Byte Master*
  - Level 6: *AI Alchemist*
- **Streaks & Streak Freeze**:
  - Tracks consecutive learning days with animated flame 🔥.
  - Includes **Streak Freeze ❄️** protection: if a student misses a day, a freeze automatically saves the streak!
- **Daily Energy Credits ⚡**:
  - 20 credits/day quota.
  - Terms cost 1 credit; scoring 2+ on quizzes rewards credits back.
- **Daily Goals**: Track daily targets (e.g. 3 terms + 1 quiz) with bonus XP rewards.
- **Badges Gallery**: 7 unlockable achievements (*First Spark*, *Bookworm*, *Quiz Wiz*, *Flame Keeper*, *Neural Cadet*, etc.).
- **History Archive**: Review previous explanations and past quiz submissions anytime.

### 4. 🛡️ School-Safe Guardrails
- **School-Safe Filter**: Blocks inappropriate content (weapons, violence, adult content, drugs, cyberbullying, malicious hacking).
- **PII Masking**: Scans for and redacts student emails, phone numbers, SSNs, and IDs with `[REDACTED_*]`.
- **Prompt Injection Defense**: Detects jailbreak attempts, DAN mode, and system prompt reveals.
- **Rate Limiting**: Sliding window rate limiter per client IP.
- **Tool Call Limiter**: Hard ceiling on agent tool invocations to prevent runaway loops.

---

## 📁 Repository Structure

```
decode_ai/
├── api/                                # FastAPI backend
│   ├── app/
│   │   ├── main.py                     # FastAPI application & CLI entrypoint
│   │   ├── config.py                   # Environment & paths configuration
│   │   ├── database.py                 # SQLite database engine (SQLModel)
│   │   ├── models/                     # DB tables & Pydantic response schemas
│   │   │   ├── db.py                   # UserProfile, Badges, Goals, History
│   │   │   └── schemas.py              # TermExplanation, QuizGrade schemas
│   │   ├── agent/                      # LangChain create_agent & tools
│   │   │   ├── agent.py                # Agent setup with response_format
│   │   │   ├── tools.py                # lookup_term, safe_web_search
│   │   │   ├── prompts.py              # System prompts for students
│   │   │   └── fake_agent.py           # Deterministic student explainer
│   │   ├── guardrails/                 # Safety & privacy filters
│   │   │   ├── school_safe.py          # Content safety filter
│   │   │   ├── pii_filter.py           # PII detection & masking
│   │   │   ├── injection.py            # Prompt injection detector
│   │   │   └── rate_limiter.py         # Rate limit & tool call limiter
│   │   └── services/                   # Business logic
│   │       ├── gamification.py         # XP, streaks, freezes, badges, goals
│   │       ├── quiz_grader.py          # 0-3 grading with feedback
│   │       └── stream.py               # SSE streaming generator
│   ├── tests/                          # 32 Pytest test cases
│   ├── pyproject.toml                  # Python dependencies managed by uv
│   └── .env.example
├── data/
│   └── glossary.json                   # 100+ Stanford HAI glossary terms
├── web/                                # Next.js frontend
│   ├── app/
│   │   ├── components/                 # Claymorphism UI components
│   │   │   ├── StatsHeader.tsx         # XP, Level, Streak, Freeze, Credits
│   │   │   ├── DailyGoalTracker.tsx    # Daily goals progress card
│   │   │   ├── SearchBar.tsx           # Search input with autocomplete
│   │   │   ├── StreamProgress.tsx      # Real-time SSE step tracker
│   │   │   ├── TermCard.tsx            # Analogy, 3 steps, example, quiz
│   │   │   ├── MentalModelSteps.tsx    # Tactile 3-step numbered cards
│   │   │   ├── QuizCard.tsx            # Interactive quiz with 0-3 stars
│   │   │   ├── HitlModal.tsx           # Human-in-the-loop search approval
│   │   │   ├── BadgesModal.tsx         # Achievements gallery
│   │   │   ├── HistoryModal.tsx        # Past explanations & quizzes
│   │   │   └── GlossaryModal.tsx       # Searchable encyclopedia
│   │   ├── globals.css                 # Claymorphism CSS utilities
│   │   ├── layout.tsx                  # Root layout
│   │   └── page.tsx                    # Main interactive page
│   ├── package.json
│   └── tailwind.config.ts
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (Python package runner)
- Node.js 18+ & npm
- (Optional) [Ollama](https://ollama.com) with `ollama pull qwen3.5:0.8b` (built-in smart student fallback included if Ollama is not installed).

---

### 1. Start the Backend API

From the repository root:

```bash
cd api
uv run fastapi dev app/main.py --port 8000
```

The FastAPI server will start at:
- **API Server**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`

#### Or Run via CLI Mode:
You can also run the explainer directly in your terminal:
```bash
cd api
uv run python app/main.py "What is RAG?"
```

---

### 2. Start the Claymorphic Frontend

In another terminal:

```bash
cd web
npm install
npm run dev
```

Open your browser at **`http://localhost:3000`** to start exploring AI terms!

---

## 🧪 Running Automated Tests

DecodeAI includes a comprehensive test suite (32 tests) verifying tools, structured outputs, school safety, PII masking, prompt injections, rate limits, streak freeze mechanics, daily goals, and SSE streaming with an offline fake model:

```bash
cd api
uv run pytest -v
```

All 32 tests run in under 10 seconds without requiring external API keys or running servers.

---

## 🎨 Claymorphism UI Showcase
- **Tactile Puffy Elements**: Multi-layered inset and outset shadows simulating soft squishy clay cards and buttons.
- **Student-Friendly Pastels**: Warm lavender, soft sky blue, gentle mint green, and peach accents.
- **Haptic Press Effects**: Buttons visibly compress on click with smooth spring transitions.
- **Reward Celebrations**: Confetti particle bursts upon mastering quizzes with a score of 3!

---

## 📄 License
MIT License. Created for students and educators exploring artificial intelligence.