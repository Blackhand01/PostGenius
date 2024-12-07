import os
import logging
import openai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")

openai.api_key = OPENAI_API_KEY

def call_openai(messages, temperature=0.7, max_tokens=200):
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
