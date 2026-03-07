import boto3
import json
import logging
import os
import random
from botocore.exceptions import ClientError
from services.voice_service import VoiceService
from config import Config # Assuming Config has BEDROCK_REGION if needed

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1' # Hardcoded region, could be from Config
        )
        self.bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0" # Or Llama 3
        self.voice_service = VoiceService()
        self.questions_bank = self._load_questions_bank()

    def _load_questions_bank(self):
        """Loads interview questions from a JSON file."""
        questions_path = os.path.join(os.path.dirname(__file__), '../data/questions_bank.json')
        if not os.path.exists(questions_path):
            logger.error(f"Questions bank not found at {questions_path}")
            return []
        with open(questions_path, 'r') as f:
            return json.load(f)

    def _pick_next_question(self, profile_json: dict, local_context_history: list, answered_question_ids: list):
        """
        Picks the next question based on profile, context, and previously answered questions.
        For simplicity, initially, it picks a random question not yet answered.
        Future: Implement matching logic based on profile skills and question keywords.
        """
        available_questions = [
            q for q in self.questions_bank if q['id'] not in answered_question_ids
        ]

        if not available_questions:
            return None # No more questions

        # Basic skill matching (can be improved)
        profile_skills = set(profile_json.get('skills', []))

        # Prioritize questions that match profile skills
        skilled_questions = []
        for q in available_questions:
            q_skills = set(q.get('skills_keywords', []))
            if profile_skills.intersection(q_skills):
                skilled_questions.append(q)

        if skilled_questions:
            return random.choice(skilled_questions)
        else:
            return random.choice(available_questions) # Fallback to any remaining question

    def _generate_response(self, question: dict, profile_json: dict, user_answer: str, local_context_history: list):
        """
        Generates a personalized response using AWS Bedrock.
        This response can be an evaluation of the user's answer, a follow-up, or the next question prompt.
        """
        system_prompt = (
            "You are a 'Ghost Recruiter' AI for Pathfinder.Ai. Your goal is to conduct "
            "technical interviews. You will receive a question you asked, the candidate's "
            "profile, their answer, and the conversation history. "
            "Your task is to provide a concise, natural language response. "
            "If the user provided an answer, you should briefly acknowledge it, "
            "and then transition to the next question. Your response should sound "
            "like a human recruiter, encouraging and professional. "
            "Keep responses under 100 words. Do NOT ask for more details on the profile. "
            "If the user_answer is empty, it means this is the first question, just introduce it."
        )

        current_question_text = question['question_text']
        history_str = "\n".join([f"{h['role']}: {h['content']}" for h in local_context_history])

        user_content = f"Candidate Profile: {json.dumps(profile_json)}\n"
        user_content += f"Current Question: {current_question_text}\n"
        if user_answer:
            user_content += f"Candidate's Answer: {user_answer}\n"
        user_content += f"Conversation History:\n{history_str}\n\n"
        user_content += "Based on the above, provide a personalized response."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300, # Sufficient for ~100 words
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "temperature": 0.7
        })

        try:
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.bedrock_model_id,
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            generated_text = response_body.get('content')[0].get('text').strip()
            return generated_text
        except ClientError as e:
            logger.error(f"Bedrock LLM invocation failed: {e}")
            return "I apologize, but I encountered an issue generating a response. Please try again."
        except Exception as e:
            logger.error(f"An unexpected error occurred during response generation: {e}")
            return "An unexpected error occurred."

    def process_interview_step(self, user_answer: str, current_phase: str, profile_json: dict, local_context_history: list, answered_question_ids: list = []):
        """
        Orchestrates the 'Pick, Think, Voice' loop for the Ghost Recruiter.
        Returns the next question, an evaluation (if any), and the audio URL for the response.
        """
        next_question = self._pick_next_question(profile_json, local_context_history, answered_question_ids)
        if not next_question:
            return {
                "next_question": None,
                "evaluation": {"summary": "Interview completed. Thank you!"},
                "audio_url": None
            }

        # If this is the first question, user_answer will be empty.
        # The LLM will generate an introduction for the first question.
        # For subsequent questions, it will acknowledge the previous answer and introduce the new question.
        recruiter_response_text = self._generate_response(next_question, profile_json, user_answer, local_context_history)

        audio_s3_key = self.voice_service.synthesize_speech(recruiter_response_text)
        audio_url = self.voice_service.get_presigned_url(audio_s3_key) if audio_s3_key else None

        # Placeholder for evaluation logic (if any for the previous answer)
        evaluation = {"summary": "Good answer. Let's move on."} if user_answer else None # Simplified

        return {
            "next_question": next_question,
            "recruiter_response_text": recruiter_response_text, # For debugging/display
            "evaluation": evaluation,
            "audio_url": audio_url
        }
