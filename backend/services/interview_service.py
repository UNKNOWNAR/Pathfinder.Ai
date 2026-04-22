import json
import os
import random
import logging
import requests

logger = logging.getLogger(__name__)

# ─── Load curated question bank once at startup ──────────────────────────────
_BANK_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions_bank.json')

def _load_question_bank():
    try:
        with open(_BANK_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load questions_bank.json: {e}")
        return {}

_QUESTION_BANK = _load_question_bank()

logger.info(
    f"Curated bank loaded: LC={len(_QUESTION_BANK.get('leetcode', []))}, "
    f"SD={len(_QUESTION_BANK.get('system_design', []))}, "
    f"BEH={len(_QUESTION_BANK.get('behavioral', []))}"
)

# Map interview topic names → bank section keys
_TOPIC_TO_BANK_KEY = {
    "data structures & algorithms": "leetcode",
    "data structures and algorithms": "leetcode",
    "algorithms": "leetcode",
    "coding": "leetcode",
    "system design": "system_design",
    "behavioral": "behavioral",
}


class InterviewService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model_id = "llama-3.3-70b-versatile"
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def _get_bank_questions(self, topic_name: str, difficulty: str, count: int) -> list:
        """
        Pull questions from the curated JSON bank if a matching section exists.
        Filters by difficulty; falls back to full section if not enough match.
        Returns properly formatted question dicts ready for the DB.
        """
        key = _TOPIC_TO_BANK_KEY.get(topic_name.lower().strip())
        if not key or key not in _QUESTION_BANK:
            return []

        pool = _QUESTION_BANK[key]

        # Try difficulty-filtered subset first
        diff_filtered = [q for q in pool if q.get("difficulty", "").lower() == difficulty.lower()]
        if len(diff_filtered) < count:
            diff_filtered = pool  # fall back to full pool

        selected = random.sample(diff_filtered, min(count, len(diff_filtered)))

        result = []
        for q in selected:
            qt = q.get("question_type", "conceptual")
            if qt not in ("coding", "behavioral", "system_design", "conceptual"):
                qt = "conceptual"

            if qt == "coding":
                title = q.get("title", "")
                starting_code = {
                    "python": f"def solution():\n    # {title}\n    pass",
                    "java": f"class Solution {{\n    // {title}\n    public void solution() {{\n    }}\n}}",
                    "cpp": f"// {title}\nvoid solution() {{\n}}",
                    "javascript": f"// {title}\nfunction solution() {{\n}}"
                }
            else:
                starting_code = {}

            result.append({
                "question_text": q.get("question_text") or q.get("title", ""),
                "question_type": qt,
                "starting_code": starting_code,
            })

        return result

    def _call_groq(self, system_prompt: str, user_prompt: str, temperature: float = 0.5, max_tokens: int = 2000) -> str | None:
        """Internal helper to call Groq API directly."""
        if not self.api_key:
            logger.error("GROQ_API_KEY is missing.")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        body = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return None

    def generate_questions(self, topic_name, difficulty, count=5):
        """
        Generate interview questions for a given topic and difficulty.
        Priority:
          1. Curated JSON bank (zero API cost, instant, randomized each session)
          2. Groq LLM fallback (for OOP, Web Dev, and topics not in the bank)
        """
        # ── 1. Try curated bank first ─────────────────────────────────────────
        bank_questions = self._get_bank_questions(topic_name, difficulty, count)
        if bank_questions:
            logger.info(
                f"Serving {len(bank_questions)} curated questions "
                f"for topic='{topic_name}' difficulty='{difficulty}'"
            )
            return bank_questions

        # ── 2. Groq LLM fallback ─────────────────────────────────────────────
        logger.info(f"No curated bank match for topic='{topic_name}'. Using Groq LLM.")
        system_prompt = (
            "You are an expert technical interviewer. Generate interview questions "
            "and return ONLY a valid JSON array. Each element must have:\n"
            '  - "question_text": the question string\n'
            '  - "question_type": one of "conceptual", "coding", or "behavioral"\n'
            '  - "starting_code": if question_type is "coding", provide a JSON object where keys are languages ("python", "java", "cpp", "javascript") and values are the starting function signature/class setup for each language. If not a coding question, return an empty object {}.\n'
            "No markdown, no commentary, just the JSON array."
        )
        user_prompt = (
            f"Generate exactly {count} {difficulty}-level interview questions "
            f"on the topic: {topic_name}. Mix conceptual, coding, and behavioral "
            f"questions where appropriate."
        )

        raw = self._call_groq(system_prompt, user_prompt, temperature=0.5, max_tokens=2000)
        if not raw:
            return []

        try:
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            parsed = json.loads(raw.strip())
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse LLM-generated questions: {e}")
            return []

    def evaluate_answer(self, question_text, question_type, voice_answer=None, code_answer=None):
        """Evaluate a student's answer using Groq LLM."""
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer. "
            "Return ONLY a valid JSON object with these keys:\n"
            '  - "score": integer 0-100\n'
            '  - "strengths": string summarizing what was done well\n'
            '  - "improvements": string with specific improvement suggestions\n'
            '  - "ideal_answer": string with a model answer\n'
            "No markdown, no commentary, just the JSON object."
        )

        answer_parts = []
        if voice_answer:
            answer_parts.append(f"Spoken answer:\n{voice_answer}")
        if code_answer:
            answer_parts.append(f"Code submission:\n{code_answer}")

        if not answer_parts:
            return {
                "score": 0,
                "strengths": "No answer provided.",
                "improvements": "Please provide either a spoken or code answer.",
                "ideal_answer": "",
            }

        user_prompt = (
            f"Question ({question_type}):\n{question_text}\n\n"
            f"Candidate's answer:\n{chr(10).join(answer_parts)}\n\n"
            f"Evaluate this answer thoroughly."
        )

        raw = self._call_groq(system_prompt, user_prompt, temperature=0.3, max_tokens=1500)
        if not raw:
            return None

        try:
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Evaluation parsing failed: {e}")
            return None
