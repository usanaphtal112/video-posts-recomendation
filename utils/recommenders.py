import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.sparse.linalg import svds
from typing import List, Optional
from .api_helpers import APIClient

from .preprocessors import DataPreprocessor
from config import Config


class RecommendationEngine:
    """
    Generates personalized video recommendations using a hybrid approach.
    """

    def __init__(self):
        """
        Initialize recommendation engine and prepare data.
        """
        self.posts_df = DataPreprocessor.preprocess_posts()
        self.user_interactions = self._load_user_interactions()
        self._prepare_content_similarity()
        self._prepare_collaborative_model()

    def _prepare_content_similarity(self):
        """
        Prepare content similarity matrix using TF-IDF.
        """
        vectorizer = TfidfVectorizer(stop_words="english")

        self.posts_df["post_summary"] = (
            self.posts_df["post_summary"].fillna("").astype(str)
        )
        self.posts_df["title"] = self.posts_df["title"].fillna("").astype(str)

        text_features = vectorizer.fit_transform(
            self.posts_df["post_summary"] + " " + self.posts_df["title"]
        )
        self.content_similarity_matrix = cosine_similarity(text_features)

    def _load_user_interactions(self):
        """
        Load or simulate user interactions data for collaborative filtering.
        Returns:
            pd.DataFrame: User interactions with posts (e.g., ratings, likes).
        """
        # Placeholder for user interaction data
        api_client = APIClient()
        user_data = api_client.fetch_paginated_data(Config.ENDPOINTS["ratings"])
        return pd.DataFrame(user_data)

    def _prepare_collaborative_model(self):
        """
        Prepare collaborative filtering matrix factorization model.
        """
        # Ensure we have a pivot table with unique user_id and post_id
        user_post_matrix = self.user_interactions.pivot_table(
            index="user_id",
            columns="post_id",
            values="rating_percent",
            aggfunc="first",  # Use first rating if multiple exist
        ).fillna(0)

        # Perform matrix factorization
        self.user_ids = user_post_matrix.index.tolist()
        self.post_ids = user_post_matrix.columns.tolist()

        user_post_matrix_sparse = user_post_matrix.values
        u, sigma, vt = svds(
            user_post_matrix_sparse, k=min(50, min(user_post_matrix_sparse.shape) - 1)
        )
        sigma = np.diag(sigma)

        self.user_factors = np.dot(u, sigma)  # User latent features
        self.post_factors = vt.T  # Post latent features

    def _collaborative_score(self, user_id: int) -> pd.Series:
        """
        Generate collaborative filtering scores for a given user.
        """
        if user_id not in self.user_ids:
            return pd.Series(0, index=self.posts_df["id"])

        user_idx = self.user_ids.index(user_id)
        scores = np.dot(self.post_factors, self.user_factors[user_idx])
        return pd.Series(scores, index=self.post_ids)

    def get_recommendations(
        self,
        username: str,
        category_id: Optional[int] = None,
        mood: Optional[str] = None,
    ) -> List[int]:
        """
        Generate personalized recommendations.

        Args:
            username (str): User identifier.
            category_id (int, optional): Specific category to filter.
            mood (str, optional): User's current mood.

        Returns:
            List[int]: List of recommended post IDs.
        """
        user_id = self._get_user_id(username)

        # Content-based scores
        content_scores = self.content_similarity_matrix.dot(
            self.posts_df["view_count"] + self.posts_df["like_count"]
        )

        # Collaborative filtering scores
        collaborative_scores = self._collaborative_score(user_id)

        # Hybrid model
        hybrid_scores = 0.6 * content_scores + 0.4 * collaborative_scores.reindex(
            self.posts_df["id"], fill_value=0
        )

        # Filter by category
        if category_id:
            category_filter = self.posts_df["category"].apply(
                lambda x: x.get("id") == category_id if x else False
            )
            hybrid_scores = hybrid_scores[category_filter.values]  # Ensure alignment

        # Sort recommendations
        recommendations = (
            hybrid_scores.sort_values(ascending=False)
            .head(Config.TOP_N_RECOMMENDATIONS)
            .index.tolist()
        )

        return recommendations

    def evaluate(self, ground_truth: pd.DataFrame = None) -> dict:
        """
        Evaluate recommendation quality using MAE and RMSE.

        Args:
            ground_truth (pd.DataFrame, optional): Actual user ratings.

        Returns:
            dict: Evaluation metrics.
        """
        # If no ground truth provided, use the existing user interactions
        if ground_truth is None:
            ground_truth = self.user_interactions

        # Ensure we have valid data
        if ground_truth.empty:
            return {"MAE": float("inf"), "RMSE": float("inf")}

        predictions = []
        actuals = []

        # Iterate through unique users
        for user_id in ground_truth["user_id"].unique():
            if user_id not in self.user_ids:
                continue

            # Get actual ratings for this user
            actual_ratings = ground_truth[ground_truth["user_id"] == user_id]

            # Get predicted ratings
            try:
                pred_ratings = self._collaborative_score(user_id)

                # Align predictions with actual ratings
                matching_preds = pred_ratings.reindex(
                    actual_ratings["post_id"], fill_value=0
                )

                predictions.extend(matching_preds.values)
                actuals.extend(actual_ratings["rating_percent"].values)
            except Exception as e:
                print(f"Error processing user {user_id}: {e}")

        # Calculate metrics if we have predictions
        if predictions and actuals:
            mae = mean_absolute_error(actuals, predictions)
            rmse = np.sqrt(mean_squared_error(actuals, predictions))
            return {"MAE": mae, "RMSE": rmse}
        else:
            return {"MAE": float("inf"), "RMSE": float("inf")}

    def _get_user_id(self, username: str) -> int:
        """
        Mock or map username to user_id for collaborative filtering.
        """
        # Placeholder mapping; replace with actual lookup
        return hash(username) % len(self.user_ids)
