import logging
import requests
import os

logger = logging.getLogger(__name__)

# Configura le credenziali per l'account Imgflip
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

def generate_meme(summary: str) -> str:
    """
    Genera un meme utilizzando l'API Imgflip basandosi sul sommario fornito.

    :param summary: Il sommario dell'articolo o testo per il meme.
    :return: URL del meme generato.
    """
    if not summary:
        logger.warning("Empty summary for meme generation.")
        return "/placeholder_meme_url.jpg"

    # Recupera i template di meme popolari da Imgflip
    template_id = _get_popular_meme_template()
    if not template_id:
        logger.error("Failed to retrieve a meme template.")
        return "/placeholder_meme_url.jpg"

    # Suddividi il sommario in due parti per il testo superiore e inferiore
    text0, text1 = _split_summary(summary)

    # Genera il meme utilizzando il template scelto
    meme_url = _create_meme(template_id, text0, text1)
    if meme_url:
        return meme_url
    else:
        logger.error("Meme generation failed.")
        return "/placeholder_meme_url.jpg"


def _get_popular_meme_template() -> str:
    """
    Recupera un template ID di un meme popolare utilizzando l'API Imgflip.

    :return: ID del template del meme.
    """
    url = "https://api.imgflip.com/get_memes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        memes = response.json().get("data", {}).get("memes", [])
        if memes:
            template_id = memes[0]["id"]  # Usa il primo template popolare
            logger.info(f"Retrieved popular meme template ID: {template_id}")
            return template_id
    except requests.RequestException as e:
        logger.exception(f"Error fetching popular memes: {e}")
    return None


def _split_summary(summary: str) -> tuple:
    """
    Suddivide il sommario in due parti: testo superiore e inferiore.

    :param summary: Il testo da suddividere.
    :return: Tuple contenente (text0, text1).
    """
    parts = summary.split(".")
    text0 = parts[0] if len(parts) > 0 else summary
    text1 = parts[1] if len(parts) > 1 else ""
    logger.debug(f"Split summary into: text0='{text0}', text1='{text1}'")
    return text0, text1


def _create_meme(template_id: str, text0: str, text1: str) -> str:
    """
    Crea un meme utilizzando l'API Imgflip.

    :param template_id: ID del template del meme.
    :param text0: Testo superiore del meme.
    :param text1: Testo inferiore del meme.
    :return: URL del meme generato.
    """
    url = "https://api.imgflip.com/caption_image"
    payload = {
        "template_id": template_id,
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": text0,
        "text1": text1,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            meme_url = result["data"]["url"]
            logger.info(f"Generated meme URL: {meme_url}")
            return meme_url
        else:
            logger.error(f"Imgflip API error: {result.get('error_message')}")
    except requests.RequestException as e:
        logger.exception(f"Error creating meme: {e}")
    return None
