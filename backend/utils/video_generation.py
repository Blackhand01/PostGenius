import logging
import os
import time
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

# RunwayML API configuration
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
RUNWAY_API_VERSION = "2024-11-06"
RUNWAY_BASE_URL = "https://api.runwayml.com/v1"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")

def generate_video_prompt_with_gpt(summary: str, prompt: str, tone: str, platform: str) -> str:
    """
    Generates a detailed prompt for video generation using GPT-4.
    
    :param summary: Summary of the content.
    :param prompt: User's original prompt.
    :param tone: Desired tone of the video.
    :return: A detailed prompt for the video.
    """
    if not summary:
        logger.warning("Summary is missing for video prompt generation.")
        return "Create a visually engaging video with a professional style."

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert in generating creative video descriptions for AI models. "
                    "Your task is to create a highly descriptive and visually engaging prompt "
                    "for a video based on the provided summary and theme."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Summary: {summary}\n"
                    f"Theme: {prompt}\n"
                    f"Tone: {tone}\n"
                    f"Platform: {platform}\n"
                    "Generate a video description that is concise, visually detailed, and aligned with the given tone."
                )
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        video_prompt = response.choices[0].message.content.strip()
        logger.info(f"Generated video prompt: {video_prompt}")
        return video_prompt
    except Exception as e:
        logger.exception(f"Error generating video prompt with GPT-4: {e}")
        return "Create a visually engaging video with a professional style."


def generate_video(prompt_text: str, prompt_image_url: str, duration: int = 10) -> str:
    """
    Generate a video using the RunwayML API.

    :param prompt_text: The descriptive text for the video.
    :param prompt_image_url: URL of the image to use as the first frame.
    :param duration: Duration of the video in seconds (default: 10).
    :return: URL of the generated video or a placeholder in case of an error.
    """
    if not prompt_text or not prompt_image_url:
        logger.warning("Prompt text or image URL is missing for video generation.")
        return "/placeholder_video_url.mp4"

    # Send the request to generate the video
    task_id = _start_video_generation(prompt_text, prompt_image_url, duration)
    if not task_id:
        logger.error("Failed to start video generation task.")
        return "/placeholder_video_url.mp4"

    # Check the task status and get the video URL
    video_url = _wait_for_video_completion(task_id)
    if video_url:
        return video_url
    else:
        logger.error("Video generation failed or timed out.")
        return "/placeholder_video_url.mp4"


def _start_video_generation(prompt_text: str, prompt_image_url: str, duration: int) -> str:
    """
    Start the video generation task using the RunwayML API.

    :param prompt_text: Descriptive text for the video.
    :param prompt_image_url: URL of the initial image.
    :param duration: Duration of the video.
    :return: Generated task ID.
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
        "watermark": False,  # Disable watermark if possible
        "ratio": "1280:768",  # Set output format
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
    Monitor the status of the video generation task until completion.

    :param task_id: ID of the video generation task.
    :param timeout: Maximum timeout in seconds (default: 300).
    :param poll_interval: Polling interval in seconds (default: 5).
    :return: URL of the generated video or None in case of an error.
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
