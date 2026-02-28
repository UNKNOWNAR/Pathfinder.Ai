import requests
import json
import logging

logger = logging.getLogger(__name__)

class LeetCodeClient:
    """
    Client for interacting with the LeetCode GraphQL API.
    Used to fetch student performance statistics for AI analysis.
    """

    BASE_URL = "https://leetcode.com/graphql"

    # The "Master Query" to fetch required student performance data
    MASTER_QUERY = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
            tagProblemCounts {
                advanced {
                    tagName
                    tagSlug
                    problemsSolved
                }
                intermediate {
                    tagName
                    tagSlug
                    problemsSolved
                }
                fundamental {
                    tagName
                    tagSlug
                    problemsSolved
                }
            }
        }
        userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            topPercentage
        }
    }
    """

    @classmethod
    def fetch_user_data(cls, username):
        """
        Fetches the user's LeetCode data using the Master Query.
        """
        try:
            payload = {
                "query": cls.MASTER_QUERY,
                "variables": {
                    "username": username
                }
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Pathfinder.Ai/1.0"
            }

            response = requests.post(cls.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                logger.error(f"LeetCode GraphQL returned errors for user {username}: {data['errors']}")
                return None

            return cls._parse_response(data.get("data", {}))

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LeetCode data for {username}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing LeetCode data for {username}: {str(e)}")
            return None

    @classmethod
    def _parse_response(cls, data):
        """
        Cleans and parses the complex nested GraphQL response into a simple,
        flattened Python dictionary/object for the AI engine.
        """
        if not data or not data.get("matchedUser"):
            return None

        matched_user = data.get("matchedUser", {})
        contest_ranking = data.get("userContestRanking", {})

        # 1. Parse submitStatsGlobal (Easy/Med/Hard completion ratios)
        difficulty_stats = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}

        submit_stats = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        for stat in submit_stats:
            difficulty = stat.get("difficulty")
            count = stat.get("count", 0)
            if difficulty in difficulty_stats:
                difficulty_stats[difficulty] = count

        # 2. Parse tagProblemCounts (Weak/Strong points)
        topics = {}
        tag_counts = matched_user.get("tagProblemCounts", {})
        
        if tag_counts:
            # Flatten the different difficulty levels of tags into one dictionary
            for level in ["fundamental", "intermediate", "advanced"]:
                for tag in tag_counts.get(level) or []:
                    tag_name = tag.get("tagName")
                    solved = tag.get("problemsSolved", 0)
                    if tag_name:
                        # If tag already exists from another level, add to it
                        topics[tag_name] = topics.get(tag_name, 0) + solved

        # Sort topics by number of problems solved (descending)
        sorted_topics = {k: v for k, v in sorted(topics.items(), key=lambda item: item[1], reverse=True)}

        # 3. Parse userContestRanking (Performance under pressure)
        contest_data = {
            "attended": contest_ranking.get("attendedContestsCount", 0) if contest_ranking else 0,
            "rating": round(contest_ranking.get("rating", 0), 2) if contest_ranking and contest_ranking.get("rating") else 0,
            "topPercentage": round(contest_ranking.get("topPercentage", 100), 2) if contest_ranking and contest_ranking.get("topPercentage") else 100
        }

        # Compile final flat object
        parsed_data = {
            "username": matched_user.get("username"),
            "total_solved": difficulty_stats.get("All", 0),
            "easy_solved": difficulty_stats.get("Easy", 0),
            "medium_solved": difficulty_stats.get("Medium", 0),
            "hard_solved": difficulty_stats.get("Hard", 0),
            "topics": sorted_topics,
            "contests": contest_data
        }

        return parsed_data
