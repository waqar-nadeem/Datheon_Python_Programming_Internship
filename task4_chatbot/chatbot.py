#!/usr/bin/env python3
"""
Rule-Based Interactive Terminal Assistant Chatbot
Python Programming Internship - Task 4

A responsive conversational assistant with multi-intent recognition.
Loads FAQs from JSON, matches user input via keywords & regex,
and provides contextual responses with graceful fallbacks.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FAQ_FILE = "sample_faq.json"
BOT_NAME = "InternBot"
EXIT_COMMANDS = {"bye", "exit", "quit", "goodbye", "see you", "cya"}


def load_faq_data(filename: str = FAQ_FILE) -> dict:
    """Load greetings and FAQ entries from a JSON file."""
    candidates = [
        Path(filename),
        Path(__file__).parent / filename,
        Path("/home/workdir/artifacts") / filename,
        Path("/home/workdir/attachments") / filename,
    ]
    for path in candidates:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)

    # Minimal fallback if JSON is missing
    return {
        "greetings": ["hello", "hi", "hey"],
        "faqs": [
            {
                "question": "What are your hours of operation?",
                "answer": "We operate Monday through Friday from 9:00 AM to 6:00 PM IST.",
            }
        ],
    }


def normalize(text: str) -> str:
    """Lowercase, strip, and collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def extract_keywords(text: str) -> set:
    """Simple keyword extraction (alphanumeric tokens of length >= 3)."""
    return {tok for tok in re.findall(r"[a-z0-9']+", text) if len(tok) >= 3}


# ---------------------------------------------------------------------------
# Intent patterns (regex + keyword sets)
# ---------------------------------------------------------------------------
# Each intent has:
#   - patterns: list of compiled regexes
#   - keywords: set of high-signal words
#   - response: callable or string
# ---------------------------------------------------------------------------

def build_intents(faq_data: dict) -> list:
    """Construct the ordered list of intents from FAQ data + built-ins."""

    intents = []

    # 1. Greeting
    greet_keywords = set(faq_data.get("greetings", []))
    intents.append({
        "name": "greeting",
        "patterns": [
            re.compile(r"\b(hi|hello|hey|good\s+(morning|afternoon|evening)|howdy)\b", re.I),
        ],
        "keywords": greet_keywords | {"greetings", "hello"},
        "response": (
            f"Hello! I'm {BOT_NAME}, your internship support assistant. "
            "How can I help you today?\n"
            "  (You can ask about hours, project submission, certificates, etc.)"
        ),
    })

    # 2. Dynamic FAQs from JSON
    for item in faq_data.get("faqs", []):
        question = item["question"]
        answer = item["answer"]
        # Build keywords from the question itself
        q_keywords = extract_keywords(normalize(question))
        # Also add a few hand-tuned signals
        extra = set()
        q_lower = question.lower()
        patterns = []
        if "hour" in q_lower or "operation" in q_lower:
            extra |= {"hours", "time", "open", "close", "schedule", "operating",
                      "opened", "opening", "timing", "available"}
            patterns.append(re.compile(
                r"\b(hours?|open|close|schedule|operating|timing)\b", re.I
            ))
        if "submit" in q_lower or "project" in q_lower:
            extra |= {"submit", "submission", "project", "github", "upload",
                      "turn", "repo", "repository", "workspace", "hand"}
            patterns.append(re.compile(
                r"\b(submit|submission|project|github|repo|upload)\b", re.I
            ))
        if "certificate" in q_lower:
            extra |= {"certificate", "cert", "certification", "diploma",
                      "completion", "receive", "issued", "get"}
            patterns.append(re.compile(
                r"\b(certificate|cert|diploma|completion)\b", re.I
            ))

        intents.append({
            "name": f"faq_{hash(question) % 10000}",
            "patterns": patterns,
            "keywords": q_keywords | extra,
            "response": answer,
            "source_question": question,
        })

    # 3. Help / capabilities
    intents.append({
        "name": "help",
        "patterns": [
            re.compile(r"\b(help|what can you do|options|commands|menu)\b", re.I),
        ],
        "keywords": {"help", "options", "commands", "menu", "assist", "support"},
        "response": (
            "I can help you with:\n"
            "  • Hours of operation\n"
            "  • How to submit your internship project\n"
            "  • Certificate issuance timeline\n"
            "  • General internship questions\n\n"
            "Just type your question, or say 'bye' to exit."
        ),
    })

    # 4. Thanks
    intents.append({
        "name": "thanks",
        "patterns": [
            re.compile(r"\b(thanks|thank you|thx|ty|appreciate)\b", re.I),
        ],
        "keywords": {"thanks", "thank", "thx", "appreciate"},
        "response": "You're welcome! Happy to help. Anything else?",
    })

    # 5. Time / date (bonus utility)
    intents.append({
        "name": "datetime",
        "patterns": [
            re.compile(r"\b(what time|current time|what'?s the time|date today)\b", re.I),
        ],
        "keywords": {"time", "date", "today", "clock"},
        "response": lambda: f"Current date & time: {datetime.now().strftime('%A, %d %B %Y  %H:%M:%S')}",
    })

    return intents


def score_intent(user_text: str, user_keywords: set, intent: dict) -> float:
    """
    Return a confidence score (0.0 – 1.0) for how well the intent matches.
    Combines regex hits and keyword overlap.
    """
    score = 0.0

    # Regex patterns (strong signal)
    for pat in intent.get("patterns", []):
        if pat.search(user_text):
            score += 0.55
            break

    # Keyword overlap – reward absolute hits more generously
    intent_kw = intent.get("keywords", set())
    if intent_kw and user_keywords:
        overlap = user_keywords & intent_kw
        if overlap:
            # Base points per matching keyword + small ratio bonus
            score += min(0.75, 0.22 * len(overlap) + 0.15 * (len(overlap) / max(len(intent_kw), 1)))

    return min(1.0, score)


def match_intent(user_text: str, intents: list, threshold: float = 0.28):
    """
    Find the best matching intent above the confidence threshold.
    Returns (intent_dict | None, confidence).
    """
    normalized = normalize(user_text)
    keywords = extract_keywords(normalized)

    best = None
    best_score = 0.0

    for intent in intents:
        s = score_intent(normalized, keywords, intent)
        if s > best_score:
            best_score = s
            best = intent

    if best_score >= threshold:
        return best, best_score
    return None, best_score


def get_response(intent: dict) -> str:
    """Resolve the response (string or callable)."""
    resp = intent["response"]
    if callable(resp):
        return resp()
    return resp


def print_bot(message: str):
    """Pretty bot output."""
    print(f"\n🤖 {BOT_NAME}: {message}")


def main():
    print("=" * 60)
    print(f"   {BOT_NAME} — Rule-Based Internship Support Assistant")
    print("=" * 60)
    print("Type your question, or 'help' to see what I can do.")
    print("Say 'bye', 'exit', or 'quit' to leave.\n")

    faq_data = load_faq_data()
    intents = build_intents(faq_data)

    # Opening greeting
    print_bot(
        f"Hi! I'm {BOT_NAME}. Ask me about internship hours, "
        "project submission, certificates, or anything related."
    )

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print_bot("Goodbye! Have a great day.")
            break

        if not user_input:
            continue

        normalized = normalize(user_input)

        # Exit check (highest priority)
        if normalized in EXIT_COMMANDS or any(
            re.search(rf"\b{re.escape(cmd)}\b", normalized) for cmd in EXIT_COMMANDS
        ):
            print_bot("Thanks for chatting! Good luck with your internship. 👋")
            break

        # Intent matching
        intent, confidence = match_intent(user_input, intents)

        if intent:
            response = get_response(intent)
            print_bot(response)
            # Optional: show confidence for debugging / transparency
            # print(f"   [confidence: {confidence:.2f}]")
        else:
            print_bot(
                "I'm not sure I understand that. "
                "You can ask about our hours, how to submit your project, "
                "or when certificates are issued. Type 'help' for more options."
            )


if __name__ == "__main__":
    main()
