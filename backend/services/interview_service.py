import json
import logging
import requests
from config import Config
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.llm_service = LLMService()

    def generate_questions(self, topic_name, difficulty, count=5):
        """Generate interview questions for a given topic and difficulty."""
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

        raw = self.llm_service.call_llm(system_prompt, user_prompt)
        if not raw:
            return []

        try:
            # Clean markdown if present
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]

            parsed = json.loads(raw.strip())
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse generated questions: {e}")
            return []

    def evaluate_answer(self, question_text, question_type, voice_answer=None, code_answer=None):
        """Evaluate a student's answer using the LLM."""
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

        raw = self.llm_service.call_llm(system_prompt, user_prompt, temperature=0.3)
        if not raw:
            return None

        try:
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Evaluation parsing failed: {e}")
            return None
