import logging
import os
import time
import requests

logger = logging.getLogger(__name__)

# Configurazione API di RunwayML
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
RUNWAY_API_VERSION = "2024-11-06"
RUNWAY_BASE_URL = "https://api.runwayml.com/v1"

def generate_video(prompt_text: str, prompt_image_url: str, duration: int = 10) -> str:
    """
    Genera un video utilizzando l'API di RunwayML.

    :param prompt_text: Il testo descrittivo per il video.
    :param prompt_image_url: URL dell'immagine da utilizzare come primo frame.
    :param duration: Durata del video in secondi (default: 10).
    :return: URL del video generato o placeholder in caso di errore.
    """
    if not prompt_text or not prompt_image_url:
        logger.warning("Prompt text or image URL is missing for video generation.")
        return "/placeholder_video_url.mp4"

    # Invia la richiesta per generare il video
    task_id = _start_video_generation(prompt_text, prompt_image_url, duration)
    if not task_id:
        logger.error("Failed to start video generation task.")
        return "/placeholder_video_url.mp4"

    # Controlla lo stato del task e ottieni l'URL del video
    video_url = _wait_for_video_completion(task_id)
    if video_url:
        return video_url
    else:
        logger.error("Video generation failed or timed out.")
        return "/placeholder_video_url.mp4"


def _start_video_generation(prompt_text: str, prompt_image_url: str, duration: int) -> str:
    """
    Avvia il task di generazione video utilizzando l'API di RunwayML.

    :param prompt_text: Testo descrittivo del video.
    :param prompt_image_url: URL dell'immagine iniziale.
    :param duration: Durata del video.
    :return: ID del task generato.
    """
    url = f"{RUNWAY_BASE_URL}/image_to_video"
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": RUNWAY_API_VERSION,
    }
    payload = {
        "model": "gen3a_turbo",
        "promptImage": prompt_image_url,
        "promptText": prompt_text,
        "duration": duration,
        "watermark": False,  # Disattiva il watermark se possibile
        "ratio": "1280:768",  # Imposta il formato di output
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        task_id = response.json().get("id")
        logger.info(f"Video generation task started. Task ID: {task_id}")
        return task_id
    except requests.RequestException as e:
        logger.exception(f"Error starting video generation task: {e}")
        return None


def _wait_for_video_completion(task_id: str, timeout: int = 300, poll_interval: int = 5) -> str:
    """
    Monitora lo stato del task di generazione video fino al completamento.

    :param task_id: ID del task di generazione video.
    :param timeout: Timeout massimo in secondi (default: 300).
    :param poll_interval: Intervallo di polling in secondi (default: 5).
    :return: URL del video generato o None in caso di errore.
    """
    url = f"{RUNWAY_BASE_URL}/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": RUNWAY_API_VERSION,
    }
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            task_data = response.json()
            status = task_data.get("status")
            logger.debug(f"Task {task_id} status: {status}")

            if status == "COMPLETED":
                video_url = task_data.get("data", {}).get("url")
                logger.info(f"Video generation completed. Video URL: {video_url}")
                return video_url
            elif status in ["FAILED", "CANCELED"]:
                logger.error(f"Task {task_id} failed with status: {status}")
                return None
        except requests.RequestException as e:
            logger.exception(f"Error checking task status: {e}")
            return None

        time.sleep(poll_interval)

    logger.error(f"Task {task_id} timed out after {timeout} seconds.")
    return None
