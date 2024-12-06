import pandas as pd
from .api_helpers import APIClient
from config import Config


class DataPreprocessor:
    """
    Handles data preprocessing for recommendation system.
    """

    @staticmethod
    def preprocess_posts() -> pd.DataFrame:
        """
        Preprocess post data from multiple endpoints.

        Returns:
            pd.DataFrame: DataFrame with processed post information.
        """
        api_client = APIClient()

        # Fetch data from different endpoints
        posts = api_client.fetch_paginated_data(Config.ENDPOINTS["posts"])
        views = api_client.fetch_paginated_data(Config.ENDPOINTS["views"])
        likes = api_client.fetch_paginated_data(Config.ENDPOINTS["likes"])
        ratings = api_client.fetch_paginated_data(Config.ENDPOINTS["ratings"])

        # Convert to DataFrames
        df_posts = pd.DataFrame(posts)
        df_views = pd.DataFrame(views)
        df_likes = pd.DataFrame(likes)
        df_ratings = pd.DataFrame(ratings)

        # print("DataFrame columns: ", df_posts.columns)
        df_posts.to_csv("posts_df.csv", index=False)
        df_views.to_csv("views_df.csv", index=False)
        df_likes.to_csv("likes_df.csv", index=False)
        df_ratings.to_csv("ratings_df.csv", index=False)
        # print("DataFrame sample: ", df_posts.head())
        # Aggregate interaction metrics
        df_posts["view_count"] = df_posts["id"].map(df_views.groupby("post_id").size())
        df_posts["like_count"] = df_posts["id"].map(df_likes.groupby("post_id").size())
        df_posts["avg_rating"] = df_posts["id"].map(
            df_ratings.groupby("post_id")["rating_percent"].mean()
        )

        # Handle missing values
        df_posts.fillna(
            {
                "view_count": 0,
                "like_count": 0,
                "avg_rating": df_posts["avg_rating"].mean(),
            },
            inplace=True,
        )

        return df_posts
