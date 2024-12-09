import logging
import openai
from openai import OpenAI
import os

# Configura il logger
logger = logging.getLogger(__name__)

# Configura la chiave API di OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)  # Assicurati di avere la libreria openai installata

def generate_image(summary: str, prompt: str, tone: str, platform: str) -> str:
    """
    Genera un'immagine utilizzando l'API DALL·E 3 basandosi su prompt, tono, piattaforma e riassunto.

    Args:
        prompt (str): Il prompt originale fornito dall'utente.
        tone (str): Il tono desiderato per l'immagine (es. "umoristico", "formale").
        platform (str): La piattaforma target (es. "Twitter", "Instagram").
        summary (str): Un riassunto dei contenuti per contestualizzare l'immagine.

    Returns:
        str: URL dell'immagine generata o un placeholder in caso di errore.
    """
    if not summary:
        logger.warning("Empty summary for image generation.")
        return "/placeholder_image_url.jpg"

    # Costruisci il prompt dettagliato per DALL·E
    detailed_prompt = (
        f"Create an illustration for a {platform} post with a {tone} tone. "
        f"Base the design on the following summary: '{summary}'. "
        f"Ensure the image aligns with the theme: '{prompt}'."
    )

    try:
        logger.debug(f"Sending request to DALL·E with detailed prompt: {detailed_prompt}")

        # Chiamata API per generare l'immagine
        response = client.images.generate(model="dall-e-3",
        prompt=detailed_prompt,
        size="1024x1024",
        quality="standard",
        n=1)

        # Estrai l'URL dell'immagine generata
        image_url = response.data[0].url
        logger.info(f"Image successfully generated: {image_url}")
        return image_url

    except openai.OpenAIError as e:
        logger.exception(f"Error generating image with DALL·E: {e}")
        return "/placeholder_image_url.jpg"
    except Exception as e:
        logger.exception(f"Unexpected error in image generation: {e}")
        return "/placeholder_image_url.jpg"  # Fallback in caso di errore
