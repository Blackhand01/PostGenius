import logging
import openai
from openai import OpenAI
import os

# Configure the logger
logger = logging.getLogger(__name__)

# Configure OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)  # Ensure the openai library is installed

def generate_image(summary: str, prompt: str, tone: str, platform: str) -> str:
    """
    Generate an image using the DALL·E 3 API based on the prompt, tone, platform, and summary.

    Args:
        prompt (str): The original prompt provided by the user.
        tone (str): The desired tone for the image (e.g., "humorous", "formal").
        platform (str): The target platform (e.g., "Twitter", "Instagram").
        summary (str): A summary of the content to contextualize the image.

    Returns:
        str: URL of the generated image or a placeholder in case of an error.
    """
    if not summary:
        logger.warning("Empty summary for image generation.")
        return "/placeholder_image_url.jpg"

    # Build the detailed prompt for DALL·E
    detailed_prompt = (
        f"Create an illustration for a {platform} post with a {tone} tone. "
        f"Base the design on the following summary: '{summary}'. "
        f"Ensure the image aligns with the theme: '{prompt}'."
    )

    try:
        logger.debug(f"Sending request to DALL·E with detailed prompt: {detailed_prompt}")

        # API call to generate the image
        response = client.images.generate(model="dall-e-3",
        prompt=detailed_prompt,
        size="1024x1024",
        quality="standard",
        n=1)

        # Extract the URL of the generated image
        image_url = response.data[0].url
        logger.info(f"Image successfully generated: {image_url}")
        return image_url

    except openai.OpenAIError as e:
        logger.exception(f"Error generating image with DALL·E: {e}")
        return "/placeholder_image_url.jpg"
    except Exception as e:
        logger.exception(f"Unexpected error in image generation: {e}")
        return "/placeholder_image_url.jpg"  # Fallback in case of error
