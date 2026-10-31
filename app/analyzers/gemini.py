"""Analyzer that reads the blueprint with Gemini (Google AI Studio)."""

import logging
import time
from collections.abc import Callable

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.prompt import EXTRACTION_PROMPT
from app.schemas import RawAnalysis


logger = logging.getLogger(__name__)

# Codes Gemini answers when it is overloaded or out of quota for now: trying again may work.
BUSY_CODES = frozenset({429, 500, 503, 504})


class GeminiAnalyzer:
    """Sends the file and the instructions to Gemini and asks for JSON with the RawAnalysis shape."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        retries: int = 0,
        retry_delay: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.model_name = model_name
        self.retries = retries
        self.retry_delay = retry_delay
        self._api_key = api_key
        self._client: genai.Client | None = None
        self._sleep = sleep

    def ready(self) -> bool:
        return bool(self._api_key)

    def _get_client(self) -> genai.Client:
        # Created on first use, so the service starts even without a key.
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def analyze(self, content: bytes, mime_type: str, floors: int) -> RawAnalysis:
        if not self.ready():
            raise AnalyzerError("GEMINI_API_KEY is not set")
        prompt = f"{EXTRACTION_PROMPT}\nThe project has {floors} floor(s)."
        busy: errors.APIError | None = None
        for attempt in range(self.retries + 1):
            if attempt:
                self._sleep(self.retry_delay)
            try:
                return self._ask(self.model_name, content, mime_type, prompt)
            except errors.APIError as ex:
                if ex.code not in BUSY_CODES:
                    raise AnalyzerError(f"Gemini answered {ex.code}: {ex.message}") from ex
                logger.warning("Gemini %s is busy (%s: %s), try %d", self.model_name, ex.code, ex.message, attempt + 1)
                busy = ex
        raise AnalyzerBusyError(f"Gemini is busy right now (it answered {busy.code}). Try again in a few minutes")

    def _ask(self, model: str, content: bytes, mime_type: str, prompt: str) -> RawAnalysis:
        response = self._get_client().models.generate_content(
            model=model,
            contents=[types.Part.from_bytes(data=content, mime_type=mime_type), prompt],
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=RawAnalysis,
            ),
        )
        return parse_answer(response.parsed, response.text)


def parse_answer(parsed: object, text: str | None) -> RawAnalysis:
    """The parsed answer, or the JSON text read again if the SDK could not parse it."""
    if isinstance(parsed, RawAnalysis):
        return parsed
    try:
        return RawAnalysis.model_validate_json(text or "")
    except ValidationError as ex:
        raise AnalyzerError("The answer of the model is not valid JSON") from ex
