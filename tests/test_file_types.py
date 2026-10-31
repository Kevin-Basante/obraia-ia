from app.file_types import JPEG, PDF, PNG, WEBP, detect_mime_type


def test_detects_pdf():
    assert detect_mime_type(b"%PDF-1.4 rest") == PDF


def test_detects_png():
    assert detect_mime_type(b"\x89PNG\r\n\x1a\n....") == PNG


def test_detects_jpeg():
    assert detect_mime_type(b"\xff\xd8\xff\xe0....") == JPEG


def test_detects_webp():
    assert detect_mime_type(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == WEBP


def test_rejects_other_files():
    assert detect_mime_type(b"PK\x03\x04 a zip file") is None


def test_rejects_short_riff_files():
    assert detect_mime_type(b"RIFF") is None
