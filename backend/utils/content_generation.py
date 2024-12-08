import os
import logging
import openai
from dotenv import load_dotenv

# Caricamento delle variabili di ambiente
load_dotenv()

# Configurazione del logger
logger = logging.getLogger(__name__)

# Chiave API di OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")

# Configurazione API
openai.api_key = OPENAI_API_KEY

def call_openai(messages, temperature=0.7, max_tokens=200):
    """
    Effettua una chiamata all'API OpenAI per ottenere un completamento di testo.

    Args:
        messages (list): Lista di messaggi per l'API ChatCompletion.
        temperature (float): Temperatura della generazione.
        max_tokens (int): Numero massimo di token nella risposta.

    Returns:
        str: Risultato generato dall'API OpenAI.
    """
    if not OPENAI_API_KEY:
        logger.error("No OPENAI_API_KEY provided, returning empty result.")
        return ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {content}")
        return content
    except Exception as e:
        logger.exception(f"Error calling OpenAI: {e}")
        return ""
def generate_social_post(summary, prompt, platform="twitter", tone="humorous"):
    """
    Genera un post per social media basato su prompt e riassunto.

    Args:
        prompt (str): Il prompt fornito dall'utente.
        summary (str): Riassunto degli articoli.
        platform (str): Piattaforma di destinazione (es. "twitter").
        tone (str): Tono desiderato (es. "humorous").

    Returns:
        str: Contenuto del post generato.
    """
    if not summary:
        logger.warning("No summary provided to generate social posts.")
        return ""

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

    return call_openai(messages)
