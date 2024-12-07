import logging
logger = logging.getLogger(__name__)

def generate_image(summary: str) -> str:
    if not summary:
        logger.warning("Empty summary for image generation.")
        return ""
    # TODO: Integrazione con DALL·E o altre API
    # Per ora ritorna placeholder
    logger.debug("Image generation placeholder invoked.")
    return "/placeholder_image_url.jpg"
