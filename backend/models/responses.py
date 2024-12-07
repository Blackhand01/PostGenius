from pydantic import BaseModel
from typing import List, Optional

class ContentResponse(BaseModel):
    text: str
    image: str
    video: str
    meme: str
    sources: Optional[List[str]] = []
