import pytest

from app.errors import ServiceError
from app.limiter import AnalysisLimiter


def test_gives_slots_up_to_the_limit():
    limiter = AnalysisLimiter(2)
    assert limiter.try_acquire()
    assert limiter.try_acquire()
    assert not limiter.try_acquire()
    assert limiter.in_use == 2


def test_released_slots_can_be_used_again():
    limiter = AnalysisLimiter(1)
    limiter.try_acquire()
    limiter.release()
    assert limiter.try_acquire()


def test_release_never_goes_below_zero():
    limiter = AnalysisLimiter(1)
    limiter.release()
    assert limiter.in_use == 0


def test_slot_frees_itself_even_after_an_error():
    limiter = AnalysisLimiter(1)
    with pytest.raises(RuntimeError), limiter.slot():
        raise RuntimeError("analysis failed")
    assert limiter.in_use == 0


def test_slot_refuses_as_busy_when_full():
    limiter = AnalysisLimiter(1)
    limiter.try_acquire()
    with pytest.raises(ServiceError) as raised, limiter.slot():
        pass
    assert (raised.value.status, raised.value.code) == (503, "ANALYZER_BUSY")
