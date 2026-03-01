from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func
from models import db
from models.job import Job
from models.profile import Profile
from models.company_question import CompanyQuestion
from services.leetcode_client import LeetCodeClient


class JobReadiness(Resource):
    @jwt_required()
    def get(self, job_id):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'message': 'Only students can view job readiness.'}, 403

        job = Job.query.get(job_id)
        if not job:
            return {'message': 'Job not found.'}, 404

        # Look up company questions using the job's company name
        company_name = job.company.strip()
        questions = CompanyQuestion.query.filter(
            func.lower(CompanyQuestion.company_name) == func.lower(company_name)
        ).all()

        if not questions:
            return {
                'message': f'No interview data available for "{company_name}".',
                'company': company_name,
                'has_data': False,
            }, 200

        # Build the company's topic breakdown
        topic_counts = {}
        difficulty_counts = {'EASY': 0, 'MEDIUM': 0, 'HARD': 0}
        for q in questions:
            diff = (q.difficulty or 'EASY').upper()
            if diff in difficulty_counts:
                difficulty_counts[diff] += 1
            for topic in (q.topics or []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Sort topics by frequency (most asked first)
        sorted_topics = dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

        # Fetch the student's LeetCode stats for comparison
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()

        student_topics = {}
        leetcode_username = None
        if profile and profile.leetcode_username:
            leetcode_username = profile.leetcode_username.strip()
            stats = LeetCodeClient.fetch_user_data(leetcode_username)
            if stats:
                student_topics = stats.get('topics', {})

        # Pre-group questions by topic so we can surface them
        questions_by_topic = {}
        for q in questions:
            for t in (q.topics or []):
                if t not in questions_by_topic:
                    questions_by_topic[t] = []
                questions_by_topic[t].append({
                    'title': q.problem_title,
                    'url': q.leetcode_url,
                    'difficulty': q.difficulty,
                    'frequency': q.frequency
                })

        # Build the comparison: for each company topic, show how many the student solved
        comparison = []
        total_company = 0
        total_student = 0
        for topic, asked_count in sorted_topics.items():
            solved = student_topics.get(topic, 0)

            # Sort topic questions by frequency
            topic_qs = sorted(questions_by_topic.get(topic, []), key=lambda x: x['frequency'], reverse=True)

            # Flag as missing if they have barely practiced this topic globally
            is_missing = solved < 10

            comparison.append({
                'topic': topic,
                'asked': asked_count,
                'solved': solved,
                'is_missing': is_missing,
                'recommended_questions': list({v["title"]: v for v in topic_qs}.values())[:3] # unique top 3 questions
            })
            total_company += asked_count
            total_student += solved

        # Calculate a simple readiness percentage
        readiness_pct = 0
        if total_company > 0 and len(sorted_topics) > 0:
            # Weight it by topic coverage, not raw counts
            covered_topics = sum(1 for t in sorted_topics if student_topics.get(t, 0) > 0)
            readiness_pct = round((covered_topics / len(sorted_topics)) * 100, 1)

        return {
            'has_data': True,
            'company': company_name,
            'total_questions': len(questions),
            'difficulty_breakdown': difficulty_counts,
            'topics': comparison[:15],  # Top 15 topics
            'readiness_pct': readiness_pct,
            'leetcode_username': leetcode_username,
        }, 200
