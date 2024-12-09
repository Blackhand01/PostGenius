import logging
import os
from openai import OpenAI
from runwayml import RunwayML
from dotenv import load_dotenv

# Configura il logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv(override=True)
# Configura le API Key
RUNWAYML_API_KEY = os.getenv("RUNWAYML_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is missing.")

if not RUNWAYML_API_KEY:
    logger.error("RUNWAY_API_SECRET is missing.")


def generate_video_prompt_with_gpt(summary: str, prompt: str, tone: str, platform: str) -> str:
    """
    Generates a detailed prompt for video generation using GPT-4o.

    :param summary: Summary of the content.
    :param prompt: User's original prompt.
    :param tone: Desired tone of the video.
    :param platform: The target platform.
    :return: A detailed prompt for the video, limited to 512 characters.
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
                    "for a video based on the provided summary and theme. The prompt must not exceed "
                    "512 UTF-16 code points in length (that is, promptText.length === 512 in JavaScript). "
                    "Be concise yet detailed, adhering to this strict character limit."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Summary: {summary}\n"
                    f"Theme: {prompt}\n"
                    f"Tone: {tone}\n"
                    f"Platform: {platform}\n"
                    "Generate a video description that is concise, visually detailed, "
                    "aligned with the given tone, and strictly under 512 characters."
                )
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        video_prompt = response.choices[0].message.content.strip()

        # Truncate the prompt to ensure it is less than 512 characters
        if len(video_prompt) > 512:
            video_prompt = video_prompt[:509] + "..."  # Add ellipsis to indicate truncation

        logger.info(f"Generated video prompt: {video_prompt}")
        return video_prompt
    except Exception as e:
        logger.exception(f"Error generating video prompt with GPT-4o: {e}")
        return "Create a visually engaging video with a professional style."


def generate_video(prompt_text: str, prompt_image_url: str, duration: int = 10) -> str:
    """
    Generate a video using the RunwayML SDK.

    :param prompt_text: The descriptive text for the video.
    :param prompt_image_url: URL of the image to use as the first frame.
    :param duration: Duration of the video in seconds (default: 10).
    :return: URL of the generated video or a placeholder in case of an error.
    """
    if not prompt_text or not prompt_image_url:
        logger.warning("Prompt text or image URL is missing for video generation.")
        return "/placeholder_video_url.mp4"

    try:
        client = RunwayML(api_key=RUNWAYML_API_KEY)
        task = client.image_to_video.create(
            model="gen3a_turbo",
            prompt_image=prompt_image_url,
            prompt_text=prompt_text,
            duration=duration,
            watermark=False,
            ratio="1280:768"
        )
        logger.info(f"Video generation task started. Task ID: {task.id}")
        
        # Wait for the task to complete
        task_result = client.tasks.retrieve(task.id)
        while task_result.status not in ["COMPLETED", "FAILED"]:
            logger.info(f"Task {task.id} is still {task_result.status}. Waiting...")
            task_result = client.tasks.retrieve(task.id)

        if task_result.status == "COMPLETED":
            video_url = task_result.data.get("url")
            logger.info(f"Video generation completed. Video URL: {video_url}")
            return video_url
        else:
            logger.error(f"Task {task.id} failed with status: {task_result.status}")
            return "/placeholder_video_url.mp4"

    except Exception as e:
        logger.exception(f"Error generating video with RunwayML: {e}")
        return "/placeholder_video_url.mp4"
