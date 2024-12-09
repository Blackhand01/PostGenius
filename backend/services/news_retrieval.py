import os
import logging
from datetime import datetime, timedelta, timezone
import requests
import hashlib
import json
from dotenv import load_dotenv
from services.groq import process_prompt_with_groq

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load keys from environment
load_dotenv(override=True)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = "PostGeniusApp/1.0"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Centralized configuration
LIMIT = 3  # Maximum number of articles
CONFIG = {
    "newsapi": {
        "page_size": LIMIT,
        "language": "en",
        "sort_by": "relevancy",
        "lookback_days": 7,
    },
    "reddit": {
        "subreddits_limit": LIMIT,
        "posts_limit": LIMIT,
    },
}


def get_relevant_articles(prompt: str, tone: str, platform: str):
    """
    Retrieve relevant articles based on a prompt, tone, and platform.
    
    Args:
        prompt (str): The search prompt.
        tone (str): The desired tone.
        platform (str): The target platform.
    
    Returns:
        list[dict]: A list of unique articles formatted for Vectara.
    """
    if not prompt:
        logger.warning("Empty prompt provided to get_relevant_articles.")
        return []

    # Process the prompt using Groq
    groq_data = process_prompt_with_groq(prompt, tone, platform)
    processed_data = {
        **groq_data,
        "original_input": {
            "tone": tone,
            "prompt": prompt,
            "platform": platform
        }
    }
    logger.debug(f"\nProcessed Data: {processed_data}")

    # Use a dictionary to avoid duplicates
    unique_articles = {}

    # Retrieve articles from NewsAPI using improved_prompt
    if NEWSAPI_KEY:
        news_articles = _get_newsapi_articles(processed_data.get("en_prompt", prompt))
        logger.debug(f"\nNewsAPI Articles Retrieved: {news_articles}")
        for article in news_articles:
            vectara_formatted = convert_to_vectara_format(article, processed_data)
            if vectara_formatted:
                unique_articles[vectara_formatted['id']] = vectara_formatted
    else:
        logger.warning("NEWSAPI_KEY is missing in environment. Skipping NewsAPI.")

    # Retrieve articles from Reddit using improved_prompt
    if REDDIT_CLIENT_ID and REDDIT_SECRET:
        reddit_articles = _get_reddit_posts(processed_data.get("en_prompt", prompt))
        logger.debug(f"\nReddit Articles Retrieved: {reddit_articles}")
        for article in reddit_articles:
            vectara_formatted = convert_to_vectara_format(article, processed_data)
            if vectara_formatted:
                unique_articles[vectara_formatted['id']] = vectara_formatted
    else:
        logger.warning("Reddit API credentials are missing in environment. Skipping Reddit.")

    # Return only unique articles
    return list(unique_articles.values())


def _get_newsapi_articles(improved_prompt: str):
    """
    Retrieve articles from NewsAPI based on an improved prompt. Accepts only the first 'LIMIT' valid articles.
    
    Args:
        improved_prompt (str): The improved prompt for a more effective search.
    
    Returns:
        list[dict]: A list of valid articles from NewsAPI.
    """
    current_date = datetime.now(timezone.utc)
    lookback_days = CONFIG["newsapi"]["lookback_days"]
    start_date = current_date - timedelta(days=lookback_days)

    params = {
        "apiKey": NEWSAPI_KEY,
        "q": improved_prompt,
        "searchIn": "title,content",
        "language": CONFIG["newsapi"]["language"],
        "sortBy": CONFIG["newsapi"]["sort_by"],
        "pageSize": CONFIG["newsapi"]["page_size"] * 3,  # Get a larger pool for filtering
        "from": start_date.isoformat(),
        "to": current_date.isoformat(),
    }

    url = "https://newsapi.org/v2/everything"
    logger.debug(f"\nNewsAPI Request: URL: {url}, Params: {params}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            logger.info(f"No articles returned for prompt: {improved_prompt} from NewsAPI.")
            return []

        # Filter valid articles
        valid_articles = []
        for article in articles:
            if (
                article.get("title") and
                (article.get("description") or article.get("content")) and
                article.get("url")
            ):
                valid_articles.append(article)
                if len(valid_articles) >= CONFIG["newsapi"]["page_size"]:
                    break

        if not valid_articles:
            logger.info(f"No valid articles found for prompt: {improved_prompt}.")
        
        return valid_articles

    except requests.RequestException as e:
        logger.exception(f"Request error to NewsAPI: {e}")
        return []


def _get_reddit_token():
    """
    Authenticate with Reddit API and retrieve an access token.
    
    Returns:
        str or None: The access token, if available. Returns None in case of an error.
    """
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": REDDIT_USER_AGENT}

    try:
        token_response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
        )
        token_response.raise_for_status()
        token = token_response.json().get("access_token")
        # logger.debug(f"\nReddit Access Token: {token}")
        return token
    except requests.RequestException as e:
        logger.exception(f"Failed to authenticate with Reddit API: {e}")
        return None

def _get_reddit_posts(improved_prompt: str):
    """
    Retrieve posts from Reddit based on an improved prompt.
    
    Args:
        improved_prompt (str): The improved prompt for a more effective search.
    
    Returns:
        list[dict]: A list of posts from Reddit. Each post includes fields such as:
                    - source (dict): Information about the source (e.g., name).
                    - author (str): The post author.
                    - title (str): The post title.
                    - description (str): The post text.
                    - url (str): The post URL.
                    - urlToImage (None): No image available for Reddit posts.
                    - publishedAt (int): Timestamp of publication.
                    - content (str): The post content.
    """
   
    token = _get_reddit_token()
    if not token:
        return []

    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": REDDIT_USER_AGENT,
    }

    url = "https://oauth.reddit.com/search"
    params = {
        "q": improved_prompt,
        "limit": CONFIG["reddit"]["posts_limit"],
        "sort": "relevance",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        posts = response.json().get("data", {}).get("children", [])

        articles = [
            {
                "source": {"id": None, "name": "Reddit"},
                "author": post["data"].get("author"),
                "title": post["data"].get("title"),
                "description": post["data"].get("selftext", ""),
                "url": post["data"].get("url"),
                "urlToImage": None,
                "publishedAt": post["data"].get("created_utc"),
                "content": post["data"].get("selftext", ""),
            }
            for post in posts
        ]
        return articles
    except requests.RequestException as e:
        logger.exception(f"Request error to Reddit API: {e}")
        return []

def convert_to_vectara_format(article: dict, processed_data: dict):
    """
    Convert an article into a format compatible with Vectara, discarding those without a source.
    
    Args:
        article (dict): The article to convert. Contains fields such as title, URL, author, and content.
        processed_data (dict): Data processed by Groq. Contains metadata and the improved prompt.
    
    Returns:
        dict or None: A dictionary formatted for Vectara or None if the article is invalid.
    """
    source = article.get("url")
    if not source:
        logger.warning("Article has no source and will be discarded.")
        return None

    unique_id = hashlib.sha256((article.get("title", "") + source).encode()).hexdigest()
    author = article.get("author", "unknown")
    category = processed_data.get("metadata", {}).get("category", "unknown")
    published_date = article.get("publishedAt", "unknown")
    if isinstance(published_date, float):  # If it is a float, convert to string
        published_date = str(published_date)
    elif not isinstance(published_date, str):  # If neither string nor float, fallback to "unknown"
        published_date = "unknown"

    published_date = published_date.split("T")[0] if "T" in published_date else published_date    
    title = article.get("title", "Untitled")
    content = article.get("description", "") + " " + article.get("content", "")
    language = "eng"  # Assume English as the default language

    # Check if content is valid
    if not content.strip():
        logger.warning(f"Article '{title}' has no valid content and will be discarded.")
        return None

    # Limit content to a maximum of 5,000 characters
    max_length = 5000
    truncated_content = content.strip()[:max_length]

    vectara_output = {
        "id": unique_id,
        "metadata": {
            "title": title,
            "lang": language,
            "category": category,
            "date": published_date,
            "author": author,
            "source": source,
        },
        "text": truncated_content,
    }

    logger.debug(f"\nVectara Formatted Output: {vectara_output}")
    return vectara_output
