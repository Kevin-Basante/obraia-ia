"""Recognizes the blueprint format by its first bytes, not by its name."""

PDF = "application/pdf"
PNG = "image/png"


def detect_mime_type(content: bytes) -> str | None:
    """MIME type of a PDF or PNG file, or None for anything else."""
    if content.startswith(b"%PDF-"):
        return PDF
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return PNG
    return None
