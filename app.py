from flask import Flask, request, jsonify
from utils.recommenders import RecommendationEngine
import pandas as pd

app = Flask(__name__)
recommendation_engine = RecommendationEngine()


@app.route("/feed", methods=["GET"])
def get_recommendations():
    """
    API endpoint for generating video recommendations

    Query Parameters:
    - username: User identifier
    - category_id (optional): Category filter
    - mood (optional): User mood

    Returns:
    JSON response with recommended post IDs
    """
    # Extract query parameters
    username = request.args.get("username")
    category_id = request.args.get("category_id", type=int)
    mood = request.args.get("mood")

    # Validate required parameters
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Generate recommendations
    try:
        recommendations = recommendation_engine.get_recommendations(
            username, category_id, mood
        )

        return jsonify(
            {
                "username": username,
                "recommended_posts": recommendations,
                "category_id": category_id,
                "mood": mood,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def get_recommendation_metrics():
    """
    API endpoint to retrieve and display recommendation evaluation metrics

    Returns:
    JSON response with MAE and RMSE metrics
    """
    try:
        # Use the existing user interactions as ground truth
        metrics = recommendation_engine.evaluate()

        # Print metrics to console
        print("Recommendation Engine Metrics:")
        print(f"Mean Absolute Error (MAE): {metrics['MAE']}")
        print(f"Root Mean Square Error (RMSE): {metrics['RMSE']}")

        # Return metrics as JSON
        return jsonify({"MAE": metrics["MAE"], "RMSE": metrics["RMSE"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(Exception)
def handle_error(e):
    """
    Global error handler
    """
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
