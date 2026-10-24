from typing import List, Optional
from app.agent.tools import GLOSSARY, lookup_term
from app.models.schemas import TermExplanation

# Curated rich explanations with 3-step mental models for common student concepts
CURATED_EXPLANATIONS = {
    "rag": TermExplanation(
        term="RAG (Retrieval-Augmented Generation)",
        simple="RAG is when an AI looks up fresh facts in a library before answering your question.",
        mental_model="RAG is like taking an open-book test instead of trying to remember every single fact from memory.",
        steps=[
            "1. You ask a question (e.g., 'What happened in the school science fair today?').",
            "2. The AI assistant flips open its notebook to find the latest notes on that exact topic.",
            "3. It combines those freshly retrieved notes with its writing skills to give a truthful answer."
        ],
        example="When a school chatbot searches your school's official student handbook PDF to tell you the deadline for homework.",
        quiz="Why is RAG like an open-book exam? A) It cheats, B) It looks up trustworthy source documents before writing the answer, C) It closes the book.",
        from_glossary=True,
        used_web_search=False,
    ),
    "llm": TermExplanation(
        term="LLM (Large Language Model)",
        simple="A giant computer program that has read millions of books and websites to predict the next best word.",
        mental_model="An LLM is like a super-powered predictive keyboard that can write entire stories and essays one word at a time.",
        steps=[
            "1. It reads your prompt and breaks each word into small puzzle pieces called tokens.",
            "2. It calculates which next word best fits the pattern of billions of sentences it studied.",
            "3. It prints that word, adds it to the sentence, and repeats to form complete ideas."
        ],
        example="Autocorrect on your phone guessing the next word you want to type, but scaled up to write code and poetry.",
        quiz="What does an LLM basically do? A) It predicts the most likely next word, B) It has conscious thoughts, C) It paints physical oil paintings.",
        from_glossary=True,
        used_web_search=False,
    ),
    "token": TermExplanation(
        term="Token",
        simple="A bite-sized chunk of letters or words that an AI model reads and writes.",
        mental_model="Tokens are like Lego bricks of language that an AI clicks together to build sentences.",
        steps=[
            "1. You type a sentence into the chat box.",
            "2. The tokenizer slices words into chunks (e.g. 'learning' -> 'learn' + 'ing').",
            "3. The AI processes these numbered chunks like beads on an abacus."
        ],
        example="The word 'cat' is usually 1 token, while long or rare words get split into 2 or 3 tokens.",
        quiz="If words are full Lego houses, what are tokens? A) The Lego bricks, B) The roof tiles only, C) The plastic box.",
        from_glossary=True,
        used_web_search=False,
    ),
    "hallucination": TermExplanation(
        term="Hallucination",
        simple="When an AI confidently makes up false information and states it as a fact.",
        mental_model="Hallucination is like a student who forgot the answer on a history quiz and invents a convincing story with confidence.",
        steps=[
            "1. The AI lacks the exact real-world knowledge in its training data or prompt.",
            "2. It focuses only on predicting words that sound smooth and grammatically convincing.",
            "3. It spits out a fictional date or made-up scientist with total confidence."
        ],
        example="An AI saying that George Washington invented the smartphone in 1776.",
        quiz="What should you do when an AI gives you important facts? A) Believe everything blindly, B) Double-check with trusted sources, C) Delete the computer.",
        from_glossary=True,
        used_web_search=False,
    ),
    "attention mechanism": TermExplanation(
        term="Attention Mechanism",
        simple="A clever trick that lets a neural network shine a spotlight on the most important words in a sentence.",
        mental_model="Attention is like using a bright yellow highlighter on the key facts in your textbook while skimming the rest.",
        steps=[
            "1. The AI looks at all the words in your sentence at the same time.",
            "2. It draws invisible connection lines, scoring which words connect closely to each other.",
            "3. When understanding 'The dog didn't cross the street because it was tired', it links 'it' directly to 'dog'."
        ],
        example="Highlighting vocabulary words in English class so you remember what they mean in context.",
        quiz="What does the attention mechanism do? A) Highlighting relevant words, B) Forcing the computer to drink coffee, C) Turning off the screen.",
        from_glossary=True,
        used_web_search=False,
    ),
}


def generate_fake_explanation(term: str, allow_web_search: bool = False) -> TermExplanation:
    """
    Generates a deterministic, high-quality student explanation for any term.
    Uses exact curated entry if known, otherwise synthesizes from GLOSSARY or fallback.
    """
    clean_term = term.strip().lower()

    # Check curated collection first
    for key, item in CURATED_EXPLANATIONS.items():
        if key in clean_term or clean_term in key:
            return item

    # Check glossary
    definition = lookup_term.invoke(clean_term)
    if definition != "NOT_FOUND":
        return TermExplanation(
            term=term.strip().title(),
            simple=f"{term.strip().title()} is an important AI concept: {definition}",
            mental_model=f"Think of {term.strip().title()} like a specialized tool in a student's study kit that solves one specific task cleanly.",
            steps=[
                f"1. A problem or input data is presented to the {term.strip().title()} system.",
                "2. The system applies learned rules and pattern matching step-by-step.",
                "3. It produces a clear, structured outcome that helps humans make better decisions."
            ],
            example=f"Using an automated {term.strip().title()} feature in educational apps to grade or organize class projects.",
            quiz=f"In simple terms, how does {term.strip().title()} help? A) By organizing patterns step-by-step, B) By turning off the power, C) By ignoring data.",
            from_glossary=True,
            used_web_search=False,
        )

    # If not found and web search allowed
    if allow_web_search:
        return TermExplanation(
            term=term.strip().title(),
            simple=f"{term.strip().title()} is an emerging technology discovered via safe educational search.",
            mental_model=f"Think of {term.strip().title()} like an exciting new club at school that just started this semester.",
            steps=[
                "1. Researchers identified a challenge that traditional software struggled to solve.",
                f"2. They designed {term.strip().title()} to learn from real-world examples and feedback.",
                "3. Now it performs tasks faster and assists people in creative new ways."
            ],
            example=f"A modern learning assistant utilizing {term.strip().title()} to answer questions accurately.",
            quiz=f"Why was {term.strip().title()} developed? A) To solve new problems using AI patterns, B) To make computers heavier, C) By accident without any goal.",
            from_glossary=False,
            used_web_search=True,
        )

    # General AI knowledge fallback
    return TermExplanation(
        term=term.strip().title(),
        simple=f"{term.strip().title()} is a specialized AI concept that helps computers learn and solve complex problems.",
        mental_model=f"{term.strip().title()} is like learning a new sport: the computer starts with basics and gets better with practice.",
        steps=[
            "1. You feed the computer examples and goal rules.",
            "2. The model adjusts its internal mathematical connections to improve accuracy.",
            "3. Over time, it learns to recognize patterns instantly without manual programming."
        ],
        example=f"How speech recognition on a tablet gets better at understanding your accent the more you talk to it.",
        quiz=f"How does an AI concept like {term.strip().title()} improve? A) Through practice and feedback, B) By staying static forever, C) By deleting its memory.",
        from_glossary=False,
        used_web_search=False,
    )
