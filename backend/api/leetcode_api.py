import logging
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from limiter import limiter
from models.profile import Profile
from services.leetcode_client import LeetCodeClient
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

def _generate_advice(stats):
    """Build a prompt from the LeetCode stats and ask the LLM for 2 sentences of advice."""
    try:
        # Identify weak topics (bottom 5)
        topics = stats.get("topics", {})
        sorted_topics = sorted(topics.items(), key=lambda x: x[1])
        weak = [t[0] for t in sorted_topics[:5]] if sorted_topics else []
        strong = [t[0] for t in sorted_topics[-3:]] if sorted_topics else []

        prompt = (
            f"A student has solved {stats['total_solved']} LeetCode problems: "
            f"{stats['easy_solved']} Easy, {stats['medium_solved']} Medium, {stats['hard_solved']} Hard. "
            f"Their weakest topics are: {', '.join(weak) if weak else 'unknown'}. "
            f"Their strongest topics are: {', '.join(strong) if strong else 'unknown'}. "
            f"Contest rating: {stats['contests']['rating']}, "
            f"top {stats['contests']['topPercentage']}%, "
            f"{stats['contests']['attended']} contests attended. "
            f"Give exactly 2 short encouraging sentences of actionable study advice for improving their DSA skills. "
            f"Be specific about which topics to focus on. Do not use bullet points or lists."
        )

        llm = LLMService()
        system_prompt = "You are a concise, encouraging coding mentor. Respond with exactly 2 sentences."
        response = llm.call_llm(system_prompt, prompt, max_tokens=150, temperature=0.7)
        return response
    except Exception as e:
        logger.error(f"AI advice generation failed: {e}")
        return None

class LeetCodeStats(Resource):
    @jwt_required()
    @limiter.limit("20 per day")
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'message': 'Only students can view LeetCode stats.'}, 403

        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()

        if not profile:
            return {'message': 'Profile not found.'}, 404

        username = profile.leetcode_username
        if not username or not username.strip():
            return {
                'message': 'No LeetCode username set. Update your profile first.',
                'no_username': True
            }, 400

        stats = LeetCodeClient.fetch_user_data(username.strip())

        if stats is None:
            return {
                'message': f'Could not fetch data for LeetCode user "{username}". Check if the username is correct.',
            }, 502

        # Generate AI advice from the stats
        advice = _generate_advice(stats)

        return {
            'stats': stats,
            'advice': advice,
        }, 200
