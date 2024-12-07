import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = "PostGeniusApp/1.0"  # Puoi personalizzarlo

def get_relevant_articles(prompt: str):
    if not prompt:
        logger.warning("Empty prompt provided to get_relevant_articles.")
        return []

    articles = []

    # Recupero articoli da NewsAPI
    if NEWSAPI_KEY:
        articles += _get_newsapi_articles(prompt)
    else:
        logger.warning("NEWSAPI_KEY is missing in environment. Skipping NewsAPI.")

    # Recupero articoli da Reddit
    if REDDIT_CLIENT_ID and REDDIT_SECRET:
        articles += _get_reddit_posts(prompt)
    else:
        logger.warning("Reddit API credentials are missing in environment. Skipping Reddit.")

    return articles

def _get_newsapi_articles(prompt: str):
    url = f"https://newsapi.org/v2/everything?q={prompt}&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
    logger.debug(f"NewsAPI URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            logger.info(f"No articles returned for prompt: {prompt} from NewsAPI.")
        return articles[:5]  # Limita a 5 articoli
    except requests.RequestException as e:
        logger.exception(f"Request error to NewsAPI: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error retrieving news from NewsAPI: {e}")
    return []

def _get_reddit_posts(prompt: str):
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": REDDIT_USER_AGENT}

    # Ottieni il token di accesso
    try:
        token_response = requests.post(
            "https://www.reddit.com/api/v1/access_token", 
            auth=auth, data=data, headers=headers
        )
        token_response.raise_for_status()
        token = token_response.json().get("access_token")
        logger.debug(f"Reddit access token obtained: {token}")
    except requests.RequestException as e:
        logger.exception(f"Failed to authenticate with Reddit API: {e}")
        return []

    # Usa il token per cercare post
    headers["Authorization"] = f"bearer {token}"
    url = f"https://oauth.reddit.com/search?q={prompt}&limit=5"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        posts = response.json().get("data", {}).get("children", [])
        
        # Log dettagliato sui post recuperati
        logger.debug(f"Number of Reddit posts retrieved: {len(posts)}")
        logger.debug(f"Raw Reddit posts data: {posts}")

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

        # Log sui dati strutturati
        logger.debug(f"Formatted Reddit articles: {articles}")
        return articles
    except requests.RequestException as e:
        logger.exception(f"Request error to Reddit API: {e}")
        return []
