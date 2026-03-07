import json
import logging
import boto3
from config import Config

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self):
        # We assume AWS credentials are set in the environment or ~/.aws/credentials
        # Using us-east-1 or us-west-2 depending on where you enable models in AWS Bedrock
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1' # Hardcoded region to simplify setup unless provided in Config
        )
        # Using Claude 4.5 Haiku for the latest speed and reasoning performance
        self.model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"

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

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.7
        })

        try:
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            raw = response_body.get('content')[0].get('text').strip()

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
            logger.error(f"Bedrock question generation failed: {e}")
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

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.3
        })

        try:
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            raw = response_body.get('content')[0].get('text').strip()

            # The model may wrap the array in markdown json blocks
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Bedrock evaluation failed: {e}")
            return None
