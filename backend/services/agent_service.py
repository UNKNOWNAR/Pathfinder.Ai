"""
Ghost Recruiter Agent Service
=============================
A stateless, event-driven AI interviewer powered by Groq LLM and browser TTS.

Architecture:
  1. Frontend sends: { user_answer, current_phase, profile_json, local_context_history, answered_question_ids, difficulty }
  2. Agent wakes up, reads the candidate Profile JSON, picks a question from questions_bank.json,
     generates a personalized recruiter response, synthesizes voice via Polly, and returns everything.
  3. Agent instantly dies. Nothing is stored in backend memory.

Phases:
  - introduction: AI reads profile, greets the user, asks them to explain a project from their resume.
  - resume_drilldown: Follow-up questions about the user's project/experience claims.
  - leetcode: Pick a coding challenge from the question bank matching user's skills.
  - system_design: Pick a system design question from the question bank.
  - behavioral: Pick a behavioral question from the question bank.
  - wrapup: Summarize the interview, give final feedback.
"""

import json
import os
import logging
from services.voice_service import VoiceService

logger = logging.getLogger(__name__)

# ─── Load questionbank once at module level ──────────────────────────────
QUESTIONS_BANK_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions_bank.json')

def _load_questions_bank():
    try:
        with open(QUESTIONS_BANK_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load questions_bank.json: {e}")
        return {"leetcode": [], "system_design": [], "behavioral": []}

QUESTIONS_BANK = _load_questions_bank()

# ─── Pre-indexed lookup tables for O(1) access ──────────────────────────
# Index by category + difficulty for instant retrieval
LOOKUP = {}
for category in ['leetcode', 'system_design', 'behavioral']:
    LOOKUP[category] = {'easy': [], 'medium': [], 'hard': [], 'all': []}
    for q in QUESTIONS_BANK.get(category, []):
        diff = q.get('difficulty', 'medium')
        LOOKUP[category][diff].append(q)
        LOOKUP[category]['all'].append(q)

# Index by topic for skill-matching (topic -> list of questions)
TOPIC_INDEX = {}
for category in ['leetcode', 'system_design', 'behavioral']:
    for q in QUESTIONS_BANK.get(category, []):
        for topic in q.get('topics', []):
            key = topic.lower()
            if key not in TOPIC_INDEX:
                TOPIC_INDEX[key] = []
            TOPIC_INDEX[key].append(q)

logger.info(f"Loaded questions bank: LC={len(QUESTIONS_BANK.get('leetcode', []))}, "
            f"SD={len(QUESTIONS_BANK.get('system_design', []))}, "
            f"BEH={len(QUESTIONS_BANK.get('behavioral', []))}, "
            f"Topics indexed: {len(TOPIC_INDEX)}")

# ─── Phase flow order ────────────────────────────────────────────────────
PHASE_ORDER = ['introduction', 'resume_drilldown', 'leetcode', 'system_design', 'behavioral', 'wrapup']


class AgentService:
    # ─── Groq — Only LLM ────────────────────────────────────────────────────
    GROQ_API_KEY   = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL     = 'llama-3.3-70b-versatile'
    GROQ_ENDPOINT  = 'https://api.groq.com/openai/v1/chat/completions'

    def __init__(self):
        self.voice_service = VoiceService()

    def process_step(self, user_answer, current_phase, profile_json, local_context_history,
                     answered_question_ids, difficulty='medium'):
        """
        The main Ghost Recruiter entry point. Called once per user interaction.
        Returns a dict with: recruiter_response_text, next_question, audio_url, next_phase, evaluation
        """
        profile = self._parse_profile(profile_json)
        candidate_name = profile.get('name', 'Candidate')

        # Determine what to do based on the current phase
        if current_phase == 'introduction':
            return self._handle_introduction(profile, candidate_name, difficulty)

        elif current_phase == 'resume_drilldown':
            return self._handle_resume_drilldown(profile, candidate_name, user_answer,
                                                  local_context_history, difficulty)

        elif current_phase == 'leetcode':
            return self._handle_leetcode(profile, candidate_name, user_answer,
                                          local_context_history, answered_question_ids, difficulty)

        elif current_phase == 'system_design':
            return self._handle_system_design(profile, candidate_name, user_answer,
                                               local_context_history, answered_question_ids, difficulty)

        elif current_phase == 'behavioral':
            return self._handle_behavioral(profile, candidate_name, user_answer,
                                            local_context_history, answered_question_ids, difficulty)

        elif current_phase == 'wrapup':
            return self._handle_wrapup(profile, candidate_name, user_answer, local_context_history)

        else:
            return self._handle_introduction(profile, candidate_name, difficulty)

    # ─── Phase Handlers ──────────────────────────────────────────────────

    def _handle_introduction(self, profile, name, difficulty):
        """Phase 1: Greet the user and ask them to explain a project from their profile."""
        projects = profile.get('projects', [])
        skills = profile.get('skills', [])
        experience = profile.get('experience', [])

        system_prompt = (
            "You are a friendly, professional Technical Recruiter at a top-tier tech company. "
            "You are conducting a 30-minute mock interview. "
            "You have the candidate's profile in front of you. "
            "Your job is to warmly greet them by name, mention something specific from their profile "
            "(a project, skill, or experience that impressed you), and then ask them to walk you through "
            "one of their projects in detail. Be conversational, warm, and encouraging. "
            "Keep your response under 100 words."
        )

        user_prompt = (
            f"Candidate Profile:\n"
            f"Name: {name}\n"
            f"Skills: {json.dumps(skills)}\n"
            f"Experience: {json.dumps(experience)}\n"
            f"Projects: {json.dumps(projects)}\n\n"
            f"Difficulty level: {difficulty}\n\n"
            f"Please greet the candidate and ask them to explain one of their projects."
        )

        recruiter_text = self._call_bedrock(system_prompt, user_prompt)
        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': {
                'id': 'intro_project',
                'question_text': recruiter_text,
                'question_type': 'behavioral',
                'starting_code': '{}'
            },
            'audio_url': audio_url,
            'next_phase': 'resume_drilldown',
            'evaluation': None
        }

    def _handle_resume_drilldown(self, profile, name, user_answer, context_history, difficulty):
        """Phase 2: Drill into the user's project explanation. Find weaknesses."""
        system_prompt = (
            "You are a Technical Recruiter conducting a mock interview. "
            "The candidate just explained one of their projects. "
            "Your job is to: 1) Briefly evaluate their explanation (1-2 sentences), "
            "2) Ask a specific follow-up question that digs deeper into a technical choice they made "
            "(e.g., 'You mentioned using S3 for storage—how did you handle access control?'). "
            "Be supportive but probe for depth. Keep your response under 80 words. "
            "Return ONLY your spoken response, no JSON."
        )

        user_prompt = self._build_context_prompt(name, profile, context_history, user_answer)
        recruiter_text = self._call_bedrock(system_prompt, user_prompt)

        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': {
                'id': 'resume_followup',
                'question_text': recruiter_text,
                'question_type': 'behavioral',
                'starting_code': '{}'
            },
            'audio_url': audio_url,
            'next_phase': 'leetcode',
            'evaluation': None
        }

    def _handle_leetcode(self, profile, name, user_answer, context_history,
                          answered_ids, difficulty):
        """Phase 3: Pick a LeetCode question matching the user's skills."""
        # Pick a question not yet answered
        question = self._pick_question('leetcode', answered_ids, difficulty, profile.get('skills', []))

        if not question:
            # Fallback: move to next phase
            return self._handle_system_design(profile, name, user_answer, context_history, answered_ids, difficulty)

        # Generate a recruiter transition
        system_prompt = (
            "You are a Technical Recruiter. You are transitioning from the resume discussion "
            "to a coding challenge. Briefly acknowledge the candidate's previous answer (1 sentence), "
            "then introduce the coding challenge naturally. "
            "Keep it under 60 words. Return ONLY your spoken words, no JSON."
        )

        user_prompt = (
            f"Candidate: {name}\n"
            f"Previous answer: {user_answer[:200] if user_answer else 'N/A'}\n"
            f"Next question title: {question['title']}\n"
            f"Next question: {question['question_text']}\n"
        )

        recruiter_text = self._call_bedrock(system_prompt, user_prompt)
        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': question,
            'audio_url': audio_url,
            'next_phase': 'system_design',
            'evaluation': None
        }

    def _handle_system_design(self, profile, name, user_answer, context_history,
                               answered_ids, difficulty):
        """Phase 4: Pick a System Design question."""
        question = self._pick_question('system_design', answered_ids, difficulty, profile.get('skills', []))

        if not question:
            return self._handle_behavioral(profile, name, user_answer, context_history, answered_ids, difficulty)

        system_prompt = (
            "You are a Technical Recruiter transitioning to a system design question. "
            "Briefly acknowledge the candidate's coding performance (1 sentence), "
            "then introduce the system design challenge. "
            "Keep it under 60 words. Return ONLY your spoken words."
        )

        user_prompt = (
            f"Candidate: {name}\n"
            f"Previous answer summary: {user_answer[:200] if user_answer else 'N/A'}\n"
            f"Next question: {question['question_text']}\n"
        )

        recruiter_text = self._call_bedrock(system_prompt, user_prompt)
        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': question,
            'audio_url': audio_url,
            'next_phase': 'behavioral',
            'evaluation': None
        }

    def _handle_behavioral(self, profile, name, user_answer, context_history,
                            answered_ids, difficulty):
        """Phase 5: Pick a Behavioral question."""
        question = self._pick_question('behavioral', answered_ids, difficulty, profile.get('skills', []))

        if not question:
            return self._handle_wrapup(profile, name, user_answer, context_history)

        system_prompt = (
            "You are a Technical Recruiter transitioning to a behavioral question. "
            "Briefly acknowledge the candidate's system design response (1 sentence), "
            "then smoothly introduce the behavioral question. "
            "Keep it under 60 words. Return ONLY your spoken words."
        )

        user_prompt = (
            f"Candidate: {name}\n"
            f"Previous answer summary: {user_answer[:200] if user_answer else 'N/A'}\n"
            f"Next question: {question['question_text']}\n"
        )

        recruiter_text = self._call_bedrock(system_prompt, user_prompt)
        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': question,
            'audio_url': audio_url,
            'next_phase': 'wrapup',
            'evaluation': None
        }

    def _handle_wrapup(self, profile, name, user_answer, context_history):
        """Phase 6: Summarize the interview and give a final, comprehensive report."""
        # Add the final answer to history for the report
        full_history = (context_history or [])
        if user_answer:
             # This is a bit hacky since we are in a stateless call, 
             # but we can simulate the final exchange for evaluation
             full_history.append({"role": "user", "content": user_answer})

        final_report = self._generate_final_report(profile, full_history)

        system_prompt = (
            "You are a Technical Recruiter wrapping up a 30-minute mock interview. "
            "Summarize the candidate's performance across all phases (project walkthrough, "
            "coding, system design, behavioral). Be encouraging but honest. "
            "Give 2-3 specific strengths and 1-2 areas for improvement. "
            "End with a warm closing statement. Keep it under 120 words. "
            "Return ONLY your spoken words."
        )

        # Build a summary of the entire conversation for the recruiter's spoken voice
        conversation_summary = "\n".join([
            f"{msg['role'].upper()}: {msg['content'][:150]}"
            for msg in (full_history)[-8:]  # Last 8 messages
        ])

        user_prompt = (
            f"Candidate: {name}\n"
            f"Conversation summary:\n{conversation_summary}\n"
            "Please provide your final spoken wrap-up."
        )

        recruiter_text = self._call_bedrock(system_prompt, user_prompt)
        audio_url = self._synthesize_and_get_url(recruiter_text)

        return {
            'recruiter_response_text': recruiter_text,
            'next_question': None,
            'audio_url': audio_url,
            'next_phase': 'completed',
            'evaluation': final_report
        }

    def _generate_final_report(self, profile, history):
        """Generate a comprehensive JSON report for the entire interview."""
        system_prompt = (
            "You are a Senior Technical Mock Interviewer. Based on the entire interview history, "
            "conduct a thorough analysis and generate a final report. "
            "Return ONLY a valid JSON object with these EXACT keys:\n"
            '  - "score": integer 0-100 (Overall performance)\n'
            '  - "strengths": string summarizing what the candidate did best\n'
            '  - "improvements": string with specific technical or behavioral advice\n'
            '  - "ideal_answer": string providing a sample perfect response to the most difficult part of the interview\n'
            "Keep the feedback professional and actionable. No markdown, no commentary."
        )

        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history
        ])

        user_prompt = (
            f"Candidate Name: {profile.get('name', 'N/A')}\n"
            f"Candidate Skills: {profile.get('skills', [])}\n"
            f"Full Interview Record:\n{history_text}\n"
            "Please generate the overall evaluation report JSON now."
        )

        try:
            raw = self._call_bedrock(system_prompt, user_prompt)
            # Cleanup markdown
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            
            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
            return {
                "score": 50,
                "strengths": "Interview completed.",
                "improvements": "System error generating detailed report.",
                "ideal_answer": "Refer to official documentation for best practices."
            }

    # ─── Helper Methods ──────────────────────────────────────────────────

    def _call_bedrock(self, system_prompt, user_prompt):
        """Call Groq API and return the text response."""
        import requests
        
        if not self.GROQ_API_KEY:
            logger.error("GROQ_API_KEY is missing.")
            return "I am currently offline due to a missing AI configuration."

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.GROQ_API_KEY}"
        }
        
        body = {
            "model": self.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.GROQ_ENDPOINT, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API call failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return "I apologize, but I am having trouble connecting to my thought engine. Could you check the API keys?"

    def _evaluate_answer(self, user_answer, question_context, context_history):
        """Evaluate the user's answer and return a score + feedback."""
        if not user_answer or not user_answer.strip():
            return {"score": 0, "strengths": "No answer provided.", "improvements": "Please provide an answer.", "ideal_answer": ""}

        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer. "
            "Return ONLY a valid JSON object with these keys:\n"
            '  - "score": integer 0-100\n'
            '  - "strengths": string summarizing what was done well\n'
            '  - "improvements": string with specific improvement suggestions\n'
            '  - "ideal_answer": string with a brief model answer\n'
            "No markdown, no commentary, just the JSON object."
        )

        user_prompt = (
            f"Question context: {question_context}\n"
            f"Candidate's answer: {user_answer}\n"
            f"Evaluate this answer thoroughly."
        )

        try:
            raw = self._call_bedrock(system_prompt, user_prompt)
            # Clean markdown wrappers
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            return json.loads(raw.strip())
        except Exception as e:
            logger.error(f"Evaluation parse failed: {e}")
            return {"score": 50, "strengths": "Answer provided.", "improvements": "Could not parse evaluation.", "ideal_answer": ""}

    def _pick_question(self, category, answered_ids, difficulty, user_skills):
        """Pick the best unanswered question from the pre-indexed bank."""
        answered_set = set(answered_ids or [])

        # Use pre-indexed LOOKUP for O(1) difficulty access
        pool = LOOKUP.get(category, {}).get(difficulty, [])
        available = [q for q in pool if q['id'] not in answered_set]

        # Fallback to all difficulties if no match
        if not available:
            pool = LOOKUP.get(category, {}).get('all', [])
            available = [q for q in pool if q['id'] not in answered_set]

        if not available:
            return None

        # Try to match user skills via topic overlap
        if user_skills:
            skill_set = set(s.lower() for s in user_skills) if isinstance(user_skills, list) else set()
            scored = []
            for q in available:
                q_topics = set(t.lower() for t in q.get('topics', []))
                overlap = len(skill_set & q_topics)
                scored.append((overlap, q.get('frequency', 0), q))
            # Sort by skill overlap first, then by interview frequency
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
            if scored[0][0] > 0:
                return scored[0][2]

        # Fallback: pick the highest-frequency unanswered question
        available.sort(key=lambda q: q.get('frequency', 0), reverse=True)
        return available[0]

    def _synthesize_and_get_url(self, text):
        """Synthesize speech and return a presigned URL."""
        try:
            s3_key = self.voice_service.synthesize_speech(text)
            if s3_key:
                return self.voice_service.get_audio_url(s3_key)
        except Exception as e:
            logger.error(f"Voice synthesis failed: {e}")
        return None

    def _parse_profile(self, profile_json):
        """Safely parse the profile JSON string."""
        if isinstance(profile_json, dict):
            return profile_json
        try:
            return json.loads(profile_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _build_context_prompt(self, name, profile, context_history, user_answer):
        """Build a context-aware prompt from the conversation history."""
        recent = (context_history or [])[-4:]  # Only last 2 exchanges (4 messages)
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content'][:150]}"
            for msg in recent
        ])

        return (
            f"Candidate: {name}\n"
            f"Skills: {json.dumps(profile.get('skills', []))}\n"
            f"Recent conversation:\n{history_text}\n"
            f"Latest answer from candidate: {user_answer}\n"
        )
