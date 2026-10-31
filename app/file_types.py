"""Recognizes the blueprint format by its first bytes, not by its name."""

PDF = "application/pdf"
PNG = "image/png"
JPEG = "image/jpeg"
WEBP = "image/webp"


def detect_mime_type(content: bytes) -> str | None:
    """MIME type of a PDF, PNG, JPEG or WEBP file, or None for anything else."""
    if content.startswith(b"%PDF-"):
        return PDF
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return PNG
    if content.startswith(b"\xff\xd8\xff"):
        return JPEG
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return WEBP
    return None
