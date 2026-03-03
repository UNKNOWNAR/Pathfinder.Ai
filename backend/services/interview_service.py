import json
import logging
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = 'llama-3.3-70b-versatile'

    def generate_questions(self, topic_name, difficulty, count=5):
        """Generate interview questions for a given topic and difficulty."""
        system_prompt = (
            "You are an expert technical interviewer. Generate interview questions "
            "and return ONLY a valid JSON array. Each element must have:\n"
            '  - "question_text": the question string\n'
            '  - "question_type": one of "conceptual", "coding", or "behavioral"\n'
            "No markdown, no commentary, just the JSON array."
        )
        user_prompt = (
            f"Generate exactly {count} {difficulty}-level interview questions "
            f"on the topic: {topic_name}. Mix conceptual, coding, and behavioral "
            f"questions where appropriate."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip()
            parsed = json.loads(raw)

            # The model may wrap the array in an object key
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        parsed = v
                        break

            return parsed
        except Exception as e:
            logger.error(f"Groq question generation failed: {e}")
            return None

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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"Groq evaluation failed: {e}")
            return None
