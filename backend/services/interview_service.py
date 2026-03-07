import json
import logging
import boto3
from config import Config

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self):
        import os
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model_id = "llama-3.3-70b-versatile"
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

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

        import requests
        if not self.api_key:
            logger.error("GROQ_API_KEY is missing.")
            return []

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
            "temperature": 0.5,
            "max_tokens": 2000
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            data = response.json()
            raw = data["choices"][0]["message"]["content"].strip()

            # The model may wrap the array in markdown json blocks
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            parsed = json.loads(raw.strip())

            # The model may wrap the array in an object key
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        parsed = v
                        break
            
            return parsed
        except Exception as e:
            logger.error(f"Error generating questions with Groq: {e}")
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

        import requests
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
            "temperature": 0.3,
            "max_tokens": 1500
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            data = response.json()
            raw = data["choices"][0]["message"]["content"].strip()

            # The model may wrap the array in markdown json blocks
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Groq evaluation failed: {e}")
            return None
