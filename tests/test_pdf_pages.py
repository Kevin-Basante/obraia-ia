from app.pdf_pages import count_pdf_pages


def pdf_with(pages: int) -> bytes:
    objects = b"".join(b"<< /Type /Page /Parent 2 0 R >>\n" for _ in range(pages))
    header = b"%PDF-1.7\n<< /Type /Pages /Count " + str(pages).encode() + b" >>\n"
    return header + objects


def test_counts_each_page_object():
    assert count_pdf_pages(pdf_with(3)) == 3


def test_the_page_tree_is_not_a_page():
    assert count_pdf_pages(b"%PDF-1.7\n<< /Type /Pages /Count 0 >>") == 0


def test_accepts_no_space_between_the_names():
    assert count_pdf_pages(b"%PDF-1.7\n<</Type/Page>>") == 1


def test_unknown_page_count_is_zero():
    assert count_pdf_pages(b"%PDF-1.7\nfake blueprint") == 0
