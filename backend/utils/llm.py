import logging
from .openai_client import call_openai

logger = logging.getLogger(__name__)

def summarize_articles(articles, tone="humorous"):
    if not articles:
        logger.warning("No articles provided to summarize.")
        return ""
    content = "\n\n".join([f"Title: {a.get('title','NoTitle')}\nDesc: {a.get('description','NoDescription')}" for a in articles])
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
        {"role": "user", "content": f"Summarize the following articles in a {tone} tone:\n{content}"}
    ]
    summary = call_openai(messages)
    if not summary:
        logger.warning("Summarization returned empty.")
    return summary

def generate_social_posts(summary, platform="twitter", tone="humorous"):
    if not summary:
        logger.warning("No summary provided to generate social posts.")
        return ""
    messages = [
        {"role": "system", "content": f"You are an expert social media content creator."},
        {"role": "user", "content": f"Create a {tone} {platform} post from this summary:\n{summary}"}
    ]
    post = call_openai(messages, max_tokens=100)
    if not post:
        logger.warning("Failed to generate social post.")
    return post
