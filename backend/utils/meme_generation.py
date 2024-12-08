import logging
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv(override=True)

# Configura il logger
logger = logging.getLogger(__name__)

# Configura le credenziali
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verifica chiave API OpenAI
if OPENAI_API_KEY is None:
    raise ValueError("La chiave API di OpenAI non è stata trovata. Assicurati di configurarla correttamente nel file .env.")

# Configura il client OpenAI
client = OpenAI()
client.api_key = OPENAI_API_KEY


def generate_meme(summary: str, tone: str, platform: str) -> str:
    """
    Genera un meme utilizzando l'API Imgflip e analizza il sommario, tono e piattaforma con OpenAI.

    :param summary: Il sommario dell'articolo o testo per il meme.
    :param tone: Il tono desiderato per il meme (es. umoristico, serio, sarcastico).
    :param platform: La piattaforma di destinazione del meme (es. Instagram, Twitter, LinkedIn).
    :return: URL del meme generato.
    """
    if not summary or not tone or not platform:
        logger.warning("Invalid input: summary, tone, or platform is missing.")
        return "/placeholder_meme_url.jpg"

    # Analizza il sommario, tono e piattaforma con OpenAI
    text0, text1 = _get_meme_text_from_summary(summary, tone, platform)

    if not text0 or not text1:
        logger.warning("Failed to generate meme text.")
        return "/placeholder_meme_url.jpg"

    # Recupera i template di meme popolari da Imgflip
    template_id = _get_popular_meme_template()
    if not template_id:
        logger.error("Failed to retrieve a meme template.")
        return "/placeholder_meme_url.jpg"

    # Genera il meme utilizzando il template scelto
    meme_url = _create_meme(template_id, text0, text1)
    if meme_url:
        return meme_url
    else:
        logger.error("Meme generation failed.")
        return "/placeholder_meme_url.jpg"


def _get_meme_text_from_summary(summary: str, tone: str, platform: str) -> tuple:
    """
    Analizza il sommario, tono e piattaforma utilizzando OpenAI per generare il testo del meme.

    :param summary: Il sommario da analizzare.
    :param tone: Il tono desiderato per il meme.
    :param platform: La piattaforma di destinazione del meme.
    :return: Tuple contenente (text0, text1).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei un generatore di meme esperto. Genera due caption brevi per un meme basato sui seguenti input."
                        " Considera il tono e la piattaforma di pubblicazione per ottimizzare il risultato."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Sommario: {summary}\n"
                        f"Tono: {tone}\n"
                        f"Piattaforma: {platform}\n"
                        "Genera due caption. La prima deve essere posizionata nella parte superiore del meme, "
                        "e la seconda nella parte inferiore.\n"
                        "Formato output:\n"
                        "Top caption: <text0>\n"
                        "Bottom caption: <text1>"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        text0 = lines[0].replace("Top caption: ", "").strip() if len(lines) > 0 else ""
        text1 = lines[1].replace("Bottom caption: ", "").strip() if len(lines) > 1 else ""

        logger.info(f"Generated captions: text0='{text0}', text1='{text1}'")
        return text0, text1
    except Exception as e:
        logger.exception(f"Error generating meme text with OpenAI: {e}")
        return "", ""


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
