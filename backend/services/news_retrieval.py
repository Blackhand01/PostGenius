import os
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Configura il logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Carica le chiavi dall'ambiente
load_dotenv(override=True)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = "PostGeniusApp/1.0"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com"

# Configurazione centralizzata
LIMIT = 1  # Limite massimo di articoli
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

def process_prompt_with_groq(prompt: str, tone: str, platform: str):
    """
    Analizza il prompt utilizzando l'API di Groq per migliorare la ricerca delle fonti.
    """
    url = f"{GROQ_BASE_URL}/process_prompt"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "tone": tone,
        "platform": platform,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        groq_data = response.json()
        logger.info(f"Groq processed prompt: {groq_data}")
        return groq_data
    except requests.RequestException as e:
        logger.exception(f"Failed to process prompt with Groq: {e}")
        return {"keywords": prompt, "metadata": {}}


def get_relevant_articles(prompt: str, tone: str, platform: str):
    if not prompt:
        logger.warning("Empty prompt provided to get_relevant_articles.")
        return []

    # Processa il prompt con Groq per arricchirlo
    groq_result = process_prompt_with_groq(prompt, tone, platform)
    enriched_prompt = groq_result.get("keywords", prompt)
    metadata = groq_result.get("metadata", {})

    articles = []

    # Recupero articoli da NewsAPI
    if NEWSAPI_KEY:
        articles += _get_newsapi_articles(enriched_prompt, metadata)
    else:
        logger.warning("NEWSAPI_KEY is missing in environment. Skipping NewsAPI.")

    # Recupero articoli da Reddit
    if REDDIT_CLIENT_ID and REDDIT_SECRET:
        articles += _get_reddit_posts(enriched_prompt, metadata)
    else:
        logger.warning("Reddit API credentials are missing in environment. Skipping Reddit.")

    return [convert_to_vectara_format(article, metadata) for article in articles]


def _get_newsapi_articles(prompt: str, metadata: dict):
    current_date = datetime.utcnow()
    lookback_days = CONFIG["newsapi"]["lookback_days"]
    start_date = current_date - timedelta(days=lookback_days)

    params = {
        "apiKey": NEWSAPI_KEY,
        "q": prompt,
        "searchIn": "title,content",
        "language": CONFIG["newsapi"]["language"],
        "sortBy": CONFIG["newsapi"]["sort_by"],
        "pageSize": CONFIG["newsapi"]["page_size"],
        "from": start_date.isoformat(),
        "to": current_date.isoformat(),
    }

    url = "https://newsapi.org/v2/everything"
    logger.debug(f"NewsAPI URL: {url}, Params: {params}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            logger.info(f"No articles returned for prompt: {prompt} from NewsAPI.")
        return articles
    except requests.RequestException as e:
        logger.exception(f"Request error to NewsAPI: {e}")
    return []


def _get_reddit_posts(prompt: str, metadata: dict):
    token = _get_reddit_token()
    if not token:
        return []

    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": REDDIT_USER_AGENT,
    }

    url = "https://oauth.reddit.com/search"
    params = {
        "q": prompt,
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


def _get_reddit_token():
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": REDDIT_USER_AGENT}

    try:
        token_response = requests.post(
            "https://www.reddit.com/api/v1/access_token", 
            auth=auth, data=data, headers=headers
        )
        token_response.raise_for_status()
        token = token_response.json().get("access_token")
        logger.debug(f"Reddit access token obtained: {token}")
        return token
    except requests.RequestException as e:
        logger.exception(f"Failed to authenticate with Reddit API: {e}")
        return None


def convert_to_vectara_format(article, metadata):
    """
    Converte un articolo nel formato compatibile con Vectara.
    Ogni frase del contenuto viene separata in base al punto.
    """
    vectara_output = {
        "documentId": article.get("documentId", "unknown"),
        "title": article.get("title", "Untitled"),
        "metadataJson": json.dumps({
            "categoria": article.get("source", {}).get("name", "unknown"),
            "data": article.get("publishedAt", "unknown"),
            "autore": article.get("author", "unknown"),
            **metadata,  # Aggiungi metadati da Groq
        }),
        "section": [],
    }

    # Controlla se c'è contenuto da processare
    content = article.get("description", "") + " " + article.get("content", "")
    if content:
        # Spezza il contenuto in frasi usando il punto come delimitatore
        sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]
        # Aggiunge ogni frase come una sezione separata
        vectara_output["section"] = [{"text": sentence} for sentence in sentences]

    return vectara_output
