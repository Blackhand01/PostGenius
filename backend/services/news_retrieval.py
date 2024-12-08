import os
import logging
from datetime import datetime, timedelta, timezone
import requests
import hashlib
import json
from dotenv import load_dotenv
from groq import Groq

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

# Inizializza il client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

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


def get_relevant_articles(prompt: str, tone: str, platform: str):
    """
    Recupera articoli rilevanti basati su un prompt, tono e piattaforma.
    
    Args:
        prompt (str): Il prompt di ricerca.
        tone (str): Il tono desiderato (es. umoristico).
        platform (str): La piattaforma target (es. Twitter).
    
    Returns:
        list[dict]: Una lista di articoli univoci formattati per Vectara.
    """
    if not prompt:
        logger.warning("Empty prompt provided to get_relevant_articles.")
        return []

    # Elabora il prompt usando Groq
    processed_data = process_prompt_with_groq(prompt, tone, platform)
    logger.debug(f"\nProcessed Data: {processed_data}")

    # Usare un dizionario per evitare duplicati
    unique_articles = {}

    # Recupero articoli da NewsAPI usando improved_prompt
    if NEWSAPI_KEY:
        news_articles = _get_newsapi_articles(processed_data.get("en_prompt", prompt))
        logger.debug(f"\nNewsAPI Articles Retrieved: {news_articles}")
        for article in news_articles:
            vectara_formatted = convert_to_vectara_format(article, processed_data)
            if vectara_formatted:
                unique_articles[vectara_formatted['id']] = vectara_formatted
    else:
        logger.warning("NEWSAPI_KEY is missing in environment. Skipping NewsAPI.")

    # Recupero articoli da Reddit usando improved_prompt
    if REDDIT_CLIENT_ID and REDDIT_SECRET:
        reddit_articles = _get_reddit_posts(processed_data.get("improved_prompt", prompt))
        logger.debug(f"\nReddit Articles Retrieved: {reddit_articles}")
        for article in reddit_articles:
            vectara_formatted = convert_to_vectara_format(article, processed_data)
            if vectara_formatted:
                unique_articles[vectara_formatted['id']] = vectara_formatted
    else:
        logger.warning("Reddit API credentials are missing in environment. Skipping Reddit.")

    # Ritorna solo articoli univoci
    return list(unique_articles.values())



def process_prompt_with_groq(prompt: str, tone: str, platform: str) -> dict:
    """
    Utilizza Groq per elaborare il prompt, tradurlo se necessario, e generare metadati.
    
    Args:
        prompt (str): Il prompt di ricerca.
        tone (str): Il tono desiderato.
        platform (str): La piattaforma target.
    
    Returns:
        dict: Un dizionario che contiene:
              - metadata (dict): Categoria e parole chiave estratte.
              - improved_prompt (str): Un prompt ottimizzato per ulteriori ricerche.
              - en_prompt (str): Il prompt tradotto in inglese per l'uso con API esterne.
              - original_input (dict): L'input originale dell'utente (tone, prompt, platform).
    """
    try:
        # Definisci il messaggio di sistema per Groq
        system_message = (
            "You are a metadata assistant. Extract relevant metadata from the user's input and return it as a JSON object in the following format:\n\n"
            "{\n"
            '  "metadata": {\n'
            '    "category": "string",\n'
            '    "keywords": ["string", "string", ...]\n'
            '  },\n'
            '  "en_prompt": "string",\n'
            '  "improved_prompt": "string",\n'
            '  "original_input": {\n'
            '    "tone": "string",\n'
            '    "prompt": "string",\n'
            '    "platform": "string"\n'
            '  }\n'
            "}\n\n"
        )
        
        # Definisci il messaggio utente includendo tutti i parametri
        user_message = f"Prompt: {prompt}\nTone: {tone}\nPlatform: {platform}"
        
        # Crea la richiesta a Groq con response_format impostato su JSON
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}, # Imposta il formato di risposta su JSON
        )
        
        # Estrai il contenuto della risposta
        metadata_str = chat_completion.choices[0].message.content.strip()
        logger.debug(f"Groq response content: {metadata_str}")
        
        # Tenta di caricare il JSON
        processed_data = json.loads(metadata_str)
        
        logger.info(f"Processed data: {processed_data}")
        return processed_data
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.exception(f"Failed to process prompt with Groq: {e}")
        # Ritorna un oggetto con original_input e metadati di fallback
        return {
            "metadata": {"category": "unknown", "keywords": []},
            "improved_prompt": prompt,  # Usa il prompt originale come fallback
            "en_prompt": prompt,  # Usa il prompt originale come fallback
            "original_input": {
                "tone": tone,
                "prompt": prompt,
                "platform": platform
            }
        }


def _get_newsapi_articles(improved_prompt: str):
    """
    Recupera articoli da NewsAPI basati su un prompt migliorato.
    
    Args:
        improved_prompt (str): Il prompt migliorato per una ricerca più efficace.
    
    Returns:
        list[dict]: Una lista di articoli da NewsAPI. Ogni articolo include campi come:
                    - source (dict): Informazioni sulla fonte.
                    - author (str): L'autore dell'articolo.
                    - title (str): Il titolo dell'articolo.
                    - description (str): La descrizione.
                    - url (str): L'URL dell'articolo.
                    - urlToImage (str): L'URL di un'immagine associata.
                    - publishedAt (str): La data di pubblicazione.
                    - content (str): Il contenuto dell'articolo.
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
        "pageSize": CONFIG["newsapi"]["page_size"],
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
        return articles
    except requests.RequestException as e:
        logger.exception(f"Request error to NewsAPI: {e}")
    return []

def _get_reddit_token():
    """
    Autentica con Reddit API e recupera un token di accesso.
    
    Returns:
        str or None: Il token di accesso, se disponibile. Restituisce None in caso di errore.
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
        logger.debug(f"\nReddit Access Token: {token}")
        return token
    except requests.RequestException as e:
        logger.exception(f"Failed to authenticate with Reddit API: {e}")
        return None

def _get_reddit_posts(improved_prompt: str):
    """
    Recupera post da Reddit basati su un prompt migliorato.
    
    Args:
        improved_prompt (str): Il prompt migliorato per una ricerca più efficace.
    
    Returns:
        list[dict]: Una lista di post da Reddit. Ogni post include campi come:
                    - source (dict): Informazioni sulla fonte (es. nome).
                    - author (str): L'autore del post.
                    - title (str): Il titolo del post.
                    - description (str): Il testo del post.
                    - url (str): L'URL del post.
                    - urlToImage (None): Nessuna immagine disponibile per i post di Reddit.
                    - publishedAt (int): Timestamp di pubblicazione.
                    - content (str): Il contenuto del post.
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
    Converte un articolo nel formato compatibile con Vectara, scartando quelli senza fonte.
    
    Args:
        article (dict): L'articolo da convertire. Contiene campi come titolo, URL, autore e contenuto.
        processed_data (dict): I dati processati da Groq. Contiene i metadati e il prompt migliorato.
    
    Returns:
        dict or None: Un dizionario formattato per Vectara o None se l'articolo è invalido.
    """
    source = article.get("url")
    if not source:
        logger.warning("Article has no source and will be discarded.")
        return None

    unique_id = hashlib.sha256((article.get("title", "") + source).encode()).hexdigest()
    author = article.get("author", "unknown")
    category = processed_data.get("metadata", {}).get("category", "unknown")
    published_date = article.get("publishedAt", "unknown")
    if isinstance(published_date, float):  # Se è un float, convertirlo in stringa
        published_date = str(published_date)
    elif not isinstance(published_date, str):  # Se non è stringa né float, fallback a "unknown"
        published_date = "unknown"

    published_date = published_date.split("T")[0] if "T" in published_date else published_date    
    title = article.get("title", "Untitled")
    content = article.get("description", "") + " " + article.get("content", "")
    language = "eng"  # Assumiamo inglese come lingua predefinita

    # Controlla se il contenuto è valido
    if not content.strip():
        logger.warning(f"Article '{title}' has no valid content and will be discarded.")
        return None

    # Limita il contenuto a un massimo di 16.000 caratteri
    max_length = 16000
    truncated_content = content.strip()[:max_length]

    vectara_output = {
        "id": unique_id,
        "metadata": {
            "title": title,
            "lang": language,
            "categoria": category,
            "data": published_date,
            "autore": author,
            "fonte": source,
        },
        "text": truncated_content,
    }

    logger.debug(f"\nVectara Formatted Output: {vectara_output}")
    return vectara_output
