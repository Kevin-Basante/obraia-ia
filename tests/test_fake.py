from app.analyzers.fake import FakeAnalyzer
from app.cleaning import clean_measurements


def test_fake_answer_is_fully_valid():
    raw = FakeAnalyzer().analyze(b"", "application/pdf", 1)
    valid, discarded = clean_measurements(raw.measurements, 1)
    assert discarded == 0
    assert len(valid) == 4


def test_fake_roof_goes_on_the_top_floor():
    raw = FakeAnalyzer().analyze(b"", "application/pdf", 2)
    assert raw.measurements[-1].floor_number == 2
