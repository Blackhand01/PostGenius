from pydantic import BaseModel

class ContentRequest(BaseModel):
    prompt: str
    tone: str = "humorous"
    platform: str = "twitter"
