import requests
from config import Config
import logging


class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.headers = {"Flic-Token": f"{Config.API_TOKEN}"}
        self.logger = logging.getLogger(__name__)

    def fetch_paginated_data(self, endpoint: str, params: dict = None) -> list:
        """
        Fetches ALL available data from an API endpoint with comprehensive pagination.

        Args:
            endpoint (str): The API endpoint (e.g., "posts/view").
            params (dict): Additional query parameters to include in the request.

        Returns:
            list: Combined data from ALL pages of the response.
        """
        if params is None:
            params = {}

        combined_data = []
        page = 1
        total_pages = float("inf")
        max_pages_to_fetch = 1000

        while page <= min(max_pages_to_fetch, total_pages):
            current_params = params.copy()
            current_params.update({"page": page, "page_size": Config.PAGE_SIZE})

            try:
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    headers=self.headers,
                    params=current_params,
                )

                if response.status_code != 200:
                    self.logger.error(
                        f"API request failed: {response.status_code} - {response.text}"
                    )
                    raise Exception(
                        f"API request failed: {response.status_code} - {response.text}"
                    )

                data = response.json()

                if data.get("status") != "success":
                    self.logger.error(
                        f"API response indicates failure: {data.get('message', 'No message')}"
                    )
                    raise Exception(
                        f"API response indicates failure: {data.get('message', 'No message')}"
                    )

                # Try to get posts from the response
                posts = data.get("posts", [])

                # Update total pages if possible (depends on API response structure)
                total_pages = data.get("total_pages", total_pages)

                # Extend combined data
                combined_data.extend(posts)

                # Stop if no more posts or fewer posts than page size
                if len(posts) < Config.PAGE_SIZE:
                    break

                page += 1

                # Log progress for large data fetches
                if page % 10 == 0:
                    self.logger.info(
                        f"Fetched {len(combined_data)} items so far from {endpoint}"
                    )

            except requests.RequestException as e:
                self.logger.error(f"Network error occurred: {e}")
                raise

        self.logger.info(f"Total items fetched from {endpoint}: {len(combined_data)}")
        return combined_data
