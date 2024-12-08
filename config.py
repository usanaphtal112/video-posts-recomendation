import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration settings for the recommendation system
    """

    API_BASE_URL = "https://api.socialverseapp.com"
    API_TOKEN = os.getenv("FLIC_TOKEN", "")

    # API Endpoints
    ENDPOINTS = {
        "posts": "posts/summary/get?page_size=1000",
        "views": "posts/view?page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
        "likes": "posts/like?page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
        "ratings": "posts/rating?page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
        "users": "users/get_all?page_size=1000",
    }

    # Pagination settings
    PAGE_SIZE = 1000
    MAX_PAGES = 5

    # Number of Recommendation settings
    TOP_N_RECOMMENDATIONS = 10
