import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_relevant_articles(prompt: str):
    if not NEWSAPI_KEY:
        logger.error("NEWSAPI_KEY is missing in environment.")
        return []
    if not prompt:
        logger.warning("Empty prompt provided to get_relevant_articles.")
        return []

    url = f"https://newsapi.org/v2/everything?q={prompt}&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
    logger.debug(f"NewsAPI URL: {url}")

    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])
        if not articles:
            logger.info(f"No articles returned for prompt: {prompt}")
        # Prende max 5 articoli
        return articles[:5]
    except requests.RequestException as e:
        logger.exception(f"Request error to NewsAPI: {e}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error retrieving news: {e}")
        return []
