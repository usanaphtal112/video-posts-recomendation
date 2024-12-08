from flask import Flask, request, jsonify
from utils.recommenders import RecommendationEngine
import pandas as pd

app = Flask(__name__)
recommendation_engine = RecommendationEngine()


@app.route("/feed", methods=["GET"])
def get_recommendations():
    """
    API endpoint for generating video recommendations
    """
    # Extract query parameters
    username = request.args.get("username")
    category_id = request.args.get("category_id", type=int)
    mood = request.args.get("mood")

    # add metrics calculation flag if needed
    calculate_metrics = request.args.get("calculate_metrics", type=bool, default=True)

    # Validate required parameters
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Generate recommendations
    try:
        recommendations = recommendation_engine.get_recommendations(
            username, category_id, mood, calculate_metrics
        )

        recommended_posts = (
            recommendation_engine.posts_df[
                recommendation_engine.posts_df["id"].isin(recommendations)
            ]
            .drop(columns=["post_summary", "baseToken"])
            .to_dict("records")
        )

        return jsonify(
            {
                "username": username,
                "recommended_posts": recommended_posts,
                "category_id": category_id,
                "mood": mood,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(Exception)
def handle_error(e):
    """
    Global error handler
    """
    return jsonify({"error": str(e)}), 500
