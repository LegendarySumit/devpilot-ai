from typing import Literal, Union
from datetime import datetime
from pydantic import BaseModel


class RendererMetadata(BaseModel):
    word_count: int = 0
    section_count: int = 0
    estimated_read_time: int = 0
    generated_at: str = None
    
    def __init__(self, **data):
        if data.get('generated_at') is None:
            data['generated_at'] = datetime.utcnow().isoformat()
        super().__init__(**data)


class RendererOutput(BaseModel):
    format: Literal["markdown", "html", "pdf", "docx", "plaintext"]
    content: Union[str, bytes]
    metadata: RendererMetadata
    
    class Config:
        arbitrary_types_allowed = True
