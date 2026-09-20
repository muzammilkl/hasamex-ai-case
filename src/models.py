from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    call_id: str
    timestamp: str
    speaker: str
    text: str