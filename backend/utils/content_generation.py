import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Caricamento delle variabili di ambiente
load_dotenv()

# Configurazione del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Chiave API di OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_social_post(summary, prompt, platform="twitter", tone="humorous", temperature=0.7, max_tokens=200):
    """
    Genera un post per social media basato su prompt e riassunto, e effettua direttamente una chiamata all'API OpenAI.

    Args:
        summary (str): Riassunto degli articoli.
        prompt (str): Il prompt fornito dall'utente.
        platform (str): Piattaforma di destinazione (es. "twitter").
        tone (str): Tono desiderato (es. "humorous").
        temperature (float): Temperatura della generazione (default: 0.7).
        max_tokens (int): Numero massimo di token nella risposta (default: 200).

    Returns:
        str: Contenuto del post generato.
    """
    if not summary:
        logger.warning("No summary provided to generate social posts.")
        return ""

    # Definizione del messaggio per OpenAI
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional content creator specialized in generating engaging social media posts. "
                "Your expertise includes creating platform-specific content with a tailored tone and style. "
                "Ensure that the outputs are concise, creative, and optimized for maximum engagement."
            )
        },
        {
            "role": "user",
            "content": (
                f"Generate a social media post for {platform} based on the following information:\n"
                f"- **Summary**: {summary}\n"
                f"- **Prompt**: {prompt}\n"
                f"- **Tone**: {tone} (e.g., humorous, formal, casual, inspiring)\n"
                f"- **Target Audience**: Social media users who are interested in {platform} trends.\n\n"
                "Guidelines:\n"
                "1. The post should be concise and engaging.\n"
                "2. Include elements like hashtags, emojis, or calls to action relevant to the platform.\n"
                "3. Ensure the tone and style match the platform and audience."
            )
        }
    ]

    try:
        # Chiamata all'API OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content.strip()
        logger.debug(f"Generated social post: {content}")
        return content
    except Exception as e:
        logger.exception(f"Error generating social post with OpenAI: {e}")
        return ""
