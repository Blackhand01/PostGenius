import logging
import requests
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure logger
logger = logging.getLogger(__name__)

# Configure credentials
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check OpenAI API key
if OPENAI_API_KEY is None:
    raise ValueError("OpenAI API key not found. Make sure it is correctly set in the .env file.")

# Configure OpenAI client
client = OpenAI()
client.api_key = OPENAI_API_KEY


def generate_meme(summary: str, prompt: str, tone: str, platform: str) -> str:
    """
    Generate a meme using the Imgflip API and analyze the summary, tone, platform, and prompt with OpenAI.

    :param summary: The article summary or text for the meme.
    :param tone: The desired tone for the meme (e.g., humorous, serious, sarcastic).
    :param platform: The target platform for the meme (e.g., Instagram, Twitter, LinkedIn).
    :param prompt: An additional message to include in the meme generation.
    :return: URL of the generated meme.
    """
    if not summary or not tone or not platform or not prompt:
        logger.warning("Invalid input: summary, tone, platform, or prompt is missing.")
        return "/placeholder_meme_url.jpg"

    # Analyze the summary, tone, platform, and prompt with OpenAI
    text0, text1 = _get_meme_text_from_summary(summary, tone, platform, prompt)

    if not text0 or not text1:
        logger.warning("Failed to generate meme text.")
        return "/placeholder_meme_url.jpg"

    # Retrieve popular meme templates from Imgflip
    template_id = _get_popular_meme_template()
    if not template_id:
        logger.error("Failed to retrieve a meme template.")
        return "/placeholder_meme_url.jpg"

    # Generate the meme using the selected template
    meme_url = _create_meme(template_id, text0, text1)
    if meme_url:
        return meme_url
    else:
        logger.error("Meme generation failed.")
        return "/placeholder_meme_url.jpg"


def _get_meme_text_from_summary(summary: str, tone: str, platform: str, prompt: str) -> tuple:
    """
    Analyze the summary, tone, platform, and prompt using OpenAI to generate meme text.

    :param summary: The summary to analyze.
    :param tone: The desired tone for the meme.
    :param platform: The target platform for the meme.
    :param prompt: An additional message to customize the meme.
    :return: Tuple containing (text0, text1).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert meme generator. Create two short captions for a meme based on the following input. "
                        "Consider the tone, publishing platform, and prompt to optimize the result."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Summary: {summary}\n"
                        f"Tone: {tone}\n"
                        f"Platform: {platform}\n"
                        f"Additional prompt: {prompt}\n"
                        "Generate two captions. The first should be positioned at the top of the meme, "
                        "and the second at the bottom. Do not use emojis in the text.\n"
                        "Output format:\n"
                        "Top caption: <text0>\n"
                        "Bottom caption: <text1>"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        text0 = _remove_emoji(lines[0].replace("Top caption: ", "").strip()) if len(lines) > 0 else ""
        text1 = _remove_emoji(lines[1].replace("Bottom caption: ", "").strip()) if len(lines) > 1 else ""

        logger.info(f"Generated captions: text0='{text0}', text1='{text1}'")
        return text0, text1
    except Exception as e:
        logger.exception(f"Error generating meme text with OpenAI: {e}")
        return "", ""


def _remove_emoji(text: str) -> str:
    """
    Remove any emojis from the text.

    :param text: The text to process.
    :return: Text without emojis.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols and pictograms
        "\U0001F680-\U0001F6FF"  # Transport and map symbols
        "\U0001F700-\U0001F77F"  # Additional symbols
        "\U0001F780-\U0001F7FF"  # Various symbols A
        "\U0001F800-\U0001F8FF"  # Various symbols B
        "\U0001F900-\U0001F9FF"  # Various symbols C
        "\U0001FA00-\U0001FA6F"  # Various symbols D
        "\U0001FA70-\U0001FAFF"  # Various symbols E
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Alphanumeric symbols
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def _get_popular_meme_template() -> str:
    """
    Retrieve a popular meme template ID using the Imgflip API.

    :return: Meme template ID.
    """
    url = "https://api.imgflip.com/get_memes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        memes = response.json().get("data", {}).get("memes", [])
        if memes:
            template_id = memes[0]["id"]  # Use the first popular template
            logger.info(f"Retrieved popular meme template ID: {template_id}")
            return template_id
    except requests.RequestException as e:
        logger.exception(f"Error fetching popular memes: {e}")
    return None


def _create_meme(template_id: str, text0: str, text1: str) -> str:
    """
    Create a meme using the Imgflip API.

    :param template_id: Meme template ID.
    :param text0: Top text for the meme.
    :param text1: Bottom text for the meme.
    :return: URL of the generated meme.
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
