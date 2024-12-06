# Recommendation System

This repository implements a recommendation system that generates personalized video recommendations based on user preferences and post interactions. Below is an explanation of how the code is structured, how to use it, and how to evaluate the system's performance.

---

## Project Structure

### 1. **Configuration (`config.py`):**
Contains all configurable settings for the recommendation system, such as API base URL, endpoints, token management, and system settings like pagination size and the number of recommendations.

- **Key Settings:**
  - `API_BASE_URL`: The base URL for the backend API.
  - `API_TOKEN`: Token for API authentication, loaded from environment variables.
  - `ENDPOINTS`: Contains all API endpoints (e.g., for posts, views, likes, ratings, and users).
  - `TOP_N_RECOMMENDATIONS`: Number of recommendations returned.

### 2. **API Helpers (`api_helpers.py`):**
Manages API communication, including paginated fetching of data and single endpoint requests.

- **Core Methods:**
  - `fetch_paginated_data`: Fetches data across multiple pages.
  - `fetch_data`: Fetches data from a single endpoint without pagination.

### 3. **Preprocessing (`preprocessors.py`):**
Handles data preparation by fetching, cleaning, and merging data from multiple endpoints into a consolidated DataFrame.

- **Core Method:**
  - `preprocess_posts`: Fetches posts, views, likes, and ratings, and processes them into a single DataFrame with aggregated metrics (view counts, like counts, average ratings).

### 4. **Recommendation Engine (`recommender.py`):**
Implements the core recommendation logic using a hybrid approach:

- **Content-Based Filtering:** Uses TF-IDF vectorization of post summaries and titles to compute cosine similarity.
- **Collaborative Filtering:** Uses matrix factorization (SVD) on user-post interaction data.
- **Hybrid Model:** Combines content-based and collaborative scores with configurable weights.
- **Evaluation:** Evaluates the system's performance using metrics like MAE (Mean Absolute Error) and RMSE (Root Mean Squared Error).

- **Core Methods:**
  - `_prepare_content_similarity`: Prepares the TF-IDF similarity matrix.
  - `_prepare_collaborative_model`: Prepares the matrix factorization model.
  - `get_recommendations`: Generates personalized recommendations based on username, category, and mood.
  - `evaluate`: Computes evaluation metrics (e.g., MAE, RMSE).

### 5. **Flask App (`app.py`):**
Provides a REST API to expose the recommendation system.

- **Endpoints:**
  - `/feed`: Accepts query parameters (username, category_id, mood) and returns a list of recommended post IDs.
  - Error handling is implemented to return informative messages in case of issues.

---

## How to Use

### 1. **Setup Environment:**
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Create a `.env` file with the API token:
  ```env
  FLIC_TOKEN=your_api_token_here
  ```

### 2. **Run the Application:**
Start the Flask app:
```bash
python app.py
```

### 3. **API Usage:**
Make a GET request to `/feed` with query parameters:
```bash
curl "http://127.0.0.1:5000/feed?username=JohnDoe&category_id=1&mood=happy"
```

### 4. **View Recommendations:**
The API returns a JSON response with recommended post IDs based on the given parameters.

---

## Metrics Evaluation

### Missing Functionality:
Currently, the code does not provide a way to:
1. Save the processed DataFrame to a CSV file.
2. View or save evaluation metrics (MAE, RMSE).

This functionality will be implemented separately.

### How Evaluation Works:
- **Inputs:** The ground truth (user-post ratings) for comparison.
- **Outputs:**
  - MAE: Measures the average absolute error between actual and predicted ratings.
  - RMSE: Measures the root mean square error for predictions.

### Additional Feature:
Once implemented, you will be able to:
1. Save the fetched and processed data as a CSV file.
2. View metrics on the console and save them to a log or file.
