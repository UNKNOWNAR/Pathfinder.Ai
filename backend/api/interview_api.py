import logging
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.interview_topic import InterviewTopic
from models.interview_session import InterviewSession
from models.interview_question import InterviewQuestion
from models.interview_evaluation import InterviewEvaluation
from services.interview_service import InterviewService

logger = logging.getLogger(__name__)

interview_service = InterviewService()

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
    for t in DEFAULT_TOPICS:
        if not InterviewTopic.query.filter_by(name=t['name']).first():
            db.session.add(InterviewTopic(**t))
    db.session.commit()


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
            user_id=get_jwt_identity(),
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
        if not session or session.user_id != get_jwt_identity():
            return {'message': 'Session not found.'}, 404
        return {'session': session.to_dict()}, 200


# ─── Questions ───────────────────────────────────────────────────────
class InterviewQuestionGenerate(Resource):
    @jwt_required()
    def post(self, session_id):
        err = _student_only()
        if err:
            return err

        session = InterviewSession.query.get(session_id)
        if not session or session.user_id != get_jwt_identity():
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
            ))
        db.session.commit()

        # Refresh to get the new questions
        db.session.refresh(session)
        return {'questions': [q.to_dict() for q in session.questions]}, 201


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
        if not session or session.user_id != get_jwt_identity():
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
