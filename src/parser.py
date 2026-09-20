import re
from pathlib import Path

from src.models import TranscriptSegment


def parse_transcript(file_path: str, call_id: str):
    """
    Read a transcript and convert it into structured segments.
    """

    text = Path(file_path).read_text(encoding="utf-8")

    pattern = r"(\d{2}:\d{2})\s*\n\s*([^:]+):\s*(.*?)(?=\n\s*\d{2}:\d{2}\s*\n|$)"

    matches = re.findall(pattern, text, re.DOTALL)

    segments = []

    for timestamp, speaker, content in matches:

        segment = TranscriptSegment(
            call_id=call_id,
            timestamp=timestamp.strip(),
            speaker=speaker.strip(),
            text=re.sub(r"\s+", " ", content).strip(),
        )

        segments.append(segment)

    return segments


def load_all_transcripts(transcripts):
    """
    Load and combine multiple transcripts.

    transcripts:
        List of tuples containing:
        (call_id, file_path)
    """

    all_segments = []

    for call_id, file_path in transcripts:

        segments = parse_transcript(
            file_path,
            call_id=call_id
        )

        all_segments.extend(segments)

    return all_segments