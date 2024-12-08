import os
import json
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
logger = logging.getLogger(__name__)

# Inizializza il client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

def process_prompt_with_groq(prompt: str, tone: str, platform: str) -> dict:
    """
    Utilizza Groq per elaborare il prompt e restituire metadati, prompt tradotto e migliorato.
    Ottimizza il prompt migliorato per la ricerca su Reddit.

    Args:
        prompt (str): Il prompt da tradurre ed elaborare.
        tone (str): Il tono desiderato.
        platform (str): La piattaforma target.

    Returns:
        dict: Contiene `metadata`, `en_prompt` e `improved_prompt`.
    """
    try:
        system_message = (
            "You are an intelligent metadata assistant. Your task is to translate the user's input into English, "
            "identify key metadata, and optimize the improved prompt for effective Reddit searches. "
            "Return your analysis in the following JSON format, ensuring clarity, completeness, and correctness:\n\n"
            "{\n"
            '  "metadata": {\n'
            '    "category": "string",\n'
            '    "keywords": ["string", "string", ...]\n'
            '  },\n'
            '  "en_prompt": "string",\n'
            '  "improved_prompt": "string"\n'
            "}\n\n"
            "For example:\n"
            "Input: 'cucina italiana'\n"
            "Output:\n"
            "{\n"
            '  "metadata": {\n'
            '    "category": "cuisine",\n'
            '    "keywords": ["Italian", "cuisine", "recipes"]\n'
            '  },\n'
            '  "en_prompt": "Italian cuisine",\n'
            '  "improved_prompt": "title:Italian cuisine OR subreddit:food OR selftext:cuisine recipes"\n'
            "}\n"
        )
        
        user_message = f"Prompt: {prompt}\nTone: {tone}\nPlatform: {platform}"
        
        # Richiesta a Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        metadata_str = chat_completion.choices[0].message.content.strip()
        logger.debug(f"Groq response content: {metadata_str}")
        
        # Parse della risposta JSON
        processed_data = json.loads(metadata_str)
        logger.info(f"Processed data: {processed_data}")
        
        return processed_data
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.exception(f"Failed to process prompt with Groq: {e}")
        # Ritorna un oggetto con valori di fallback
        return {
            "metadata": {"category": "unknown", "keywords": []},
            "en_prompt": prompt,  # Usa il prompt originale come fallback
            "improved_prompt": f"title:{prompt} OR subreddit:all"  # Usa una query base ottimizzata per Reddit come fallback
        }
