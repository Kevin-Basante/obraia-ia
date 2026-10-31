"""Analyzer that reads the blueprint with Gemini (Google AI Studio)."""

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.analyzers.base import AnalyzerError
from app.prompt import EXTRACTION_PROMPT
from app.schemas import RawAnalysis


class GeminiAnalyzer:
    """Sends the file and the instructions to Gemini and asks for JSON with the RawAnalysis shape."""

    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        self._api_key = api_key
        self._client: genai.Client | None = None

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
        try:
            response = self._get_client().models.generate_content(
                model=self.model_name,
                contents=[types.Part.from_bytes(data=content, mime_type=mime_type), prompt],
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=RawAnalysis,
                ),
            )
        except errors.APIError as ex:
            raise AnalyzerError(f"Gemini answered {ex.code}: {ex.message}") from ex
        return parse_answer(response.parsed, response.text)


def parse_answer(parsed: object, text: str | None) -> RawAnalysis:
    """The parsed answer, or the JSON text read again if the SDK could not parse it."""
    if isinstance(parsed, RawAnalysis):
        return parsed
    try:
        return RawAnalysis.model_validate_json(text or "")
    except ValidationError as ex:
        raise AnalyzerError("The answer of the model is not valid JSON") from ex
