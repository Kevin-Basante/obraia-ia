"""Counts the pages of a PDF without opening it with a PDF library."""

import re

# Each page object says "/Type /Page"; the page tree says "/Type /Pages", which is not counted.
_PAGE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")


def count_pdf_pages(content: bytes) -> int:
    """Pages found in the PDF, or 0 when they cannot be seen (for example, compressed object streams)."""
    return len(_PAGE.findall(content))
