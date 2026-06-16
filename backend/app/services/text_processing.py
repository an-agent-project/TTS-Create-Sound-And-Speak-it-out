import re

from app.models import PreprocessResponse, SensitiveHit, TextSegment

SENSITIVE_WORDS = ["暴力", "色情", "赌博", "毒品", "诈骗", "恐怖"]

PAUSE_BY_ENDING = {
    "。": 700,
    "！": 750,
    "？": 750,
    "；": 500,
    ";": 500,
    "，": 300,
    ",": 300,
    ".": 600,
    "!": 700,
    "?": 700,
}


def clean_text(content: str) -> str:
    text = content.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_segments(content: str, max_length: int = 120) -> list[TextSegment]:
    cleaned = clean_text(content)
    if not cleaned:
        return []

    raw_parts = re.split(r"(?<=[。！？!?；;，,\n])", cleaned)
    segments: list[TextSegment] = []
    buffer = ""

    def flush(value: str) -> None:
        piece = value.strip()
        if not piece:
            return
        while len(piece) > max_length:
            split_at = _find_split_index(piece, max_length)
            _append_segment(segments, piece[:split_at].strip())
            piece = piece[split_at:].strip()
        if piece:
            _append_segment(segments, piece)

    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if len(buffer) + len(part) <= max_length:
            buffer += part
        else:
            flush(buffer)
            buffer = part
    flush(buffer)
    return segments


def find_sensitive_words(content: str) -> list[SensitiveHit]:
    hits: list[SensitiveHit] = []
    for word in SENSITIVE_WORDS:
        start = 0
        while True:
            index = content.find(word, start)
            if index == -1:
                break
            hits.append(SensitiveHit(word=word, index=index))
            start = index + len(word)
    return sorted(hits, key=lambda hit: hit.index)


def preprocess_text(content: str, max_segment_length: int = 120) -> PreprocessResponse:
    cleaned = clean_text(content)
    return PreprocessResponse(
        cleanedText=cleaned,
        segments=split_segments(cleaned, max_segment_length),
        sensitiveWords=find_sensitive_words(cleaned),
    )


def _find_split_index(text: str, max_length: int) -> int:
    candidates = ["，", ",", "、", " "]
    for mark in candidates:
        idx = text.rfind(mark, 0, max_length)
        if idx > max_length * 0.45:
            return idx + 1
    return max_length


def _append_segment(segments: list[TextSegment], text: str) -> None:
    pause = PAUSE_BY_ENDING.get(text[-1], 250) if text else 250
    segments.append(TextSegment(index=len(segments), text=text, pauseMs=pause))
