import json
import logging
from flask import send_file
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.interview_topic import InterviewTopic
from models.interview_session import InterviewSession
from models.interview_question import InterviewQuestion
from models.interview_evaluation import InterviewEvaluation
from services.interview_service import InterviewService
from services.voice_service import VoiceService
from services.agent_service import AgentService # Import AgentService
import io
from limiter import limiter

logger = logging.getLogger(__name__)

interview_service = InterviewService()
voice_service = VoiceService()
agent_service = AgentService() # Initialize AgentService

# ─── Seed default topics on import ───────────────────────────────────
DEFAULT_TOPICS = [
    {'name': 'Data Structures & Algorithms', 'category': 'technical',
     'description': 'Arrays, trees, graphs, sorting, dynamic programming'},
    {'name': 'System Design', 'category': 'technical',
     'description': 'Scalability, load balancing, database design, caching'},
    {'name': 'Object-Oriented Programming', 'category': 'technical',
     'description': 'Classes, inheritance, polymorphism, design patterns'},
    {'name': 'Web Development', 'category': 'technical',
     'description': 'HTTP, REST APIs, frontend/backend, databases'},
    {'name': 'Behavioral', 'category': 'behavioral',
     'description': 'Teamwork, leadership, conflict resolution, communication'},
]


def seed_interview_topics():
    try:
        for t in DEFAULT_TOPICS:
            if not InterviewTopic.query.filter_by(name=t['name']).first():
                db.session.add(InterviewTopic(**t))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
# ─── Helper ──────────────────────────────────────────────────────────
def _student_only():
    claims = get_jwt()
    if claims.get('role') != 'student':
        return {'message': 'Only students can access interviews.'}, 403
    return None


# ─── Topics ──────────────────────────────────────────────────────────
class InterviewTopicList(Resource):
    @jwt_required()
    def get(self):
        err = _student_only()
        if err:
            return err
        topics = InterviewTopic.query.all()
        return {'topics': [t.to_dict() for t in topics]}, 200


# ─── Sessions ────────────────────────────────────────────────────────
class InterviewSessionCreate(Resource):
    @jwt_required()
    def post(self):
        err = _student_only()
        if err:
            return err

        parser = reqparse.RequestParser()
        parser.add_argument('topic_id', type=int, required=True)
        parser.add_argument('difficulty', type=str, default='medium')
        args = parser.parse_args()

        topic = InterviewTopic.query.get(args['topic_id'])
        if not topic:
            return {'message': 'Topic not found.'}, 404

        session = InterviewSession(
            user_id=int(get_jwt_identity()),
            topic_id=args['topic_id'],
            difficulty=args['difficulty'],
        )
        db.session.add(session)
        db.session.commit()
        return {'session': session.to_dict()}, 201


class InterviewSessionDetail(Resource):
    @jwt_required()
    def get(self, session_id):
        err = _student_only()
        if err:
            return err

        session = InterviewSession.query.get(session_id)
        if not session or session.user_id != int(get_jwt_identity()):
            return {'message': 'Session not found.'}, 404
        return {'session': session.to_dict()}, 200


# ─── Questions ───────────────────────────────────────────────────────
class InterviewQuestionGenerate(Resource):
    @jwt_required()
    @limiter.limit("20 per day")
    def post(self, session_id):
        err = _student_only()
        if err:
            return err

        session = InterviewSession.query.get(session_id)
        if not session or session.user_id != int(get_jwt_identity()):
            return {'message': 'Session not found.'}, 404

        # Don't regenerate if questions already exist
        if session.questions:
            return {'questions': [q.to_dict() for q in session.questions]}, 200

        parser = reqparse.RequestParser()
        parser.add_argument('count', type=int, default=5)
        args = parser.parse_args()

        questions_data = interview_service.generate_questions(
            topic_name=session.topic.name,
            difficulty=session.difficulty,
            count=args['count'],
        )
        if questions_data is None:
            return {'message': 'Failed to generate questions. Please try again.'}, 502

        for i, q in enumerate(questions_data):
            db.session.add(InterviewQuestion(
                session_id=session.session_id,
                order_index=i,
                question_text=q.get('question_text', ''),
                question_type=q.get('question_type', 'conceptual'),
                starting_code=json.dumps(q.get('starting_code', {})) if isinstance(q.get('starting_code'), dict) else q.get('starting_code', '')
            ))
        db.session.commit()

        # Refresh to get the new questions
        db.session.refresh(session)
        return {'questions': [q.to_dict() for q in session.questions]}, 201


class InterviewQuestionAudio(Resource):
    @jwt_required()
    def get(self, question_id):
        err = _student_only()
        if err:
            return err

        question = InterviewQuestion.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404

        session = InterviewSession.query.get(question.session_id)
        if not session or session.user_id != int(get_jwt_identity()):
            return {'message': 'Not authorized.'}, 403

        try:
            # We use boto3 polly client directly inside the VoiceService to get the bytes if synthesize_speech does not return bytes.
            # But the VoiceService was just modified to return S3 URL by the user, so let's check it.
            # Based on the user changes:
            s3_key = voice_service.synthesize_speech(question.question_text)
            if not s3_key:
                return {'message': 'Failed to generate audio.'}, 500

            # Since the frontend expects audio bytes from this endpoint in the way we wrote it earlier (blob),
            # we should either fetch it from S3 and return the bytes, or return the presigned URL and let frontend download it.
            # Let's fetch the object from S3 and return the bytes to keep compatibility with the frontend blob logic.
            import boto3
            s3_client = boto3.client('s3')
            response = s3_client.get_object(Bucket=voice_service.bucket_name, Key=s3_key)
            audio_bytes = response['Body'].read()

            return send_file(
                io.BytesIO(audio_bytes),
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name=f"question_{question_id}.mp3"
            )
        except Exception as e:
            logger.error(f"Failed to generate audio for question {question_id}: {e}")
            return {'message': 'Failed to generate audio.'}, 500


# ─── Answer Submission ───────────────────────────────────────────────
class InterviewAnswerSubmit(Resource):
    @jwt_required()
    def post(self, question_id):
        err = _student_only()
        if err:
            return err

        question = InterviewQuestion.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404

        # Verify ownership
        session = InterviewSession.query.get(question.session_id)
        if not session or session.user_id != int(get_jwt_identity()):
            return {'message': 'Not authorized.'}, 403

        # Don't re-evaluate
        if question.evaluation:
            return {'evaluation': question.evaluation.to_dict()}, 200

        parser = reqparse.RequestParser()
        parser.add_argument('voice_answer', type=str, default='')
        parser.add_argument('code_answer', type=str, default='')
        args = parser.parse_args()

        result = interview_service.evaluate_answer(
            question_text=question.question_text,
            question_type=question.question_type,
            voice_answer=args['voice_answer'],
            code_answer=args['code_answer'],
        )
        if result is None:
            return {'message': 'Evaluation failed. Please try again.'}, 502

        evaluation = InterviewEvaluation(
            question_id=question.question_id,
            voice_answer=args['voice_answer'] or None,
            code_answer=args['code_answer'] or None,
            score=result.get('score', 0),
            strengths=result.get('strengths', ''),
            improvements=result.get('improvements', ''),
            ideal_answer=result.get('ideal_answer', ''),
        )
        db.session.add(evaluation)

        # Check if all questions in the session are now evaluated
        all_evaluated = all(
            q.evaluation is not None or q.question_id == question.question_id
            for q in session.questions
        )
        if all_evaluated:
            session.status = 'completed'

        db.session.commit()
        return {'evaluation': evaluation.to_dict()}, 201


# ─── Ghost Recruiter Endpoint ─────────────────────────────────────────
class GhostInterviewStep(Resource):
    @jwt_required()
    @limiter.limit("100 per hour")
    def post(self):
        err = _student_only()
        if err:
            return err

        parser = reqparse.RequestParser()
        parser.add_argument('user_answer', type=str, default='')
        parser.add_argument('current_phase', type=str, default='introduction')
        parser.add_argument('profile_json', type=str, required=True)
        parser.add_argument('local_context_history', type=list, default=[], location='json')
        parser.add_argument('answered_question_ids', type=list, default=[], location='json')
        parser.add_argument('difficulty', type=str, default='medium')

        args = parser.parse_args()

        try:
            profile_data = json.loads(args['profile_json'])
        except (json.JSONDecodeError, TypeError):
            # If it's already a dict (e.g., from JSON body), use it directly
            profile_data = args['profile_json'] if isinstance(args['profile_json'], dict) else {}

        result = agent_service.process_step(
            user_answer=args['user_answer'],
            current_phase=args['current_phase'],
            profile_json=profile_data,
            local_context_history=args['local_context_history'] or [],
            answered_question_ids=args['answered_question_ids'] or [],
            difficulty=args['difficulty']
        )
        return result, 200

