import re

import jieba

from app.work_schemas import PreprocessResponse, SensitiveHit, TextSegment

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

PARAGRAPH_PAUSE_MS = 900
WORD_BOUNDARY_PAUSE_MS = 120

MIN_SPLIT_RATIO = 0.45
PREFERRED_BREAK_MARKS = "，,；;：:、 "
CLOSING_PUNCTUATION = "，。！？；：、,.!?;:)]}）】》”’」』"
OPENING_PUNCTUATION = "([{（【《“‘「『"


def clean_text(content: str) -> str:
    text = content.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_segments(content: str, max_length: int = 120, pause_scale: float = 1.0) -> list[TextSegment]:
    cleaned = clean_text(content)
    if not cleaned:
        return []

    segments: list[TextSegment] = []

    for paragraph in re.split(r"\n+", cleaned):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        paragraph_start = len(segments)
        buffer = ""
        sentences = re.findall(r".*?[。！？!?；;](?:[”’」』])?|.+$", paragraph)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if buffer and len(buffer) + len(sentence) > max_length:
                _flush_piece(segments, buffer, max_length, pause_scale)
                buffer = ""
            buffer += sentence
            if len(buffer) >= max_length:
                _flush_piece(segments, buffer, max_length, pause_scale)
                buffer = ""

        _flush_piece(segments, buffer, max_length, pause_scale)
        if len(segments) > paragraph_start:
            segments[-1].pauseMs = max(segments[-1].pauseMs, round(PARAGRAPH_PAUSE_MS * pause_scale))

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


def preprocess_text(content: str, max_segment_length: int = 120, pause_scale: float = 1.0) -> PreprocessResponse:
    cleaned = clean_text(content)
    return PreprocessResponse(
        cleanedText=cleaned,
        segments=split_segments(cleaned, max_segment_length, pause_scale),
        sensitiveWords=find_sensitive_words(cleaned),
    )


def _find_split_index(text: str, max_length: int) -> int:
    for mark in PREFERRED_BREAK_MARKS:
        idx = text.rfind(mark, 0, max_length)
        if idx > max_length * MIN_SPLIT_RATIO:
            return idx + 1

    candidates = _word_boundary_candidates(text, max_length)
    if candidates:
        return candidates[-1]

    # Only an individual token longer than max_length reaches this fallback.
    return max_length


def _word_boundary_candidates(text: str, max_length: int) -> list[int]:
    candidates: list[int] = []
    for _, start, end in jieba.tokenize(text, mode="default"):
        if end > max_length:
            break
        if end <= max_length * MIN_SPLIT_RATIO:
            continue
        if text[end - 1] in OPENING_PUNCTUATION:
            continue
        if end < len(text) and text[end] in CLOSING_PUNCTUATION:
            continue
        candidates.append(end)
    return candidates


def _flush_piece(segments: list[TextSegment], value: str, max_length: int, pause_scale: float) -> None:
    piece = value.strip()
    while len(piece) > max_length:
        split_at = _find_split_index(piece, max_length)
        _append_segment(segments, piece[:split_at].strip(), pause_scale)
        piece = piece[split_at:].strip()
    if piece:
        _append_segment(segments, piece, pause_scale)


def _append_segment(segments: list[TextSegment], text: str, pause_scale: float = 1.0) -> None:
    pause = PAUSE_BY_ENDING.get(text[-1], WORD_BOUNDARY_PAUSE_MS) if text else WORD_BOUNDARY_PAUSE_MS
    pause = max(0, round(pause * pause_scale))
    segments.append(TextSegment(index=len(segments), text=text, pauseMs=pause))
