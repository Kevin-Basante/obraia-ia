"""Summary writer that asks Gemini (Google AI Studio)."""

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.analyzers.base import AnalyzerBusyError, AnalyzerError
from app.analyzers.gemini import BUSY_CODES
from app.reports.prompt import summary_prompt
from app.reports.schemas import RawSummary, SummaryRequest


class GeminiSummaryWriter:
    """Sends the figures and the instructions to one Gemini model and asks for JSON with the RawSummary shape."""

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

    def write(self, request: SummaryRequest) -> RawSummary:
        if not self.ready():
            raise AnalyzerError("GEMINI_API_KEY is not set")
        prompt = summary_prompt(
            request.language, request.report_type, request.figures.model_dump_json(exclude_none=True)
        )
        try:
            response = self._get_client().models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=RawSummary,
                ),
            )
        except errors.APIError as ex:
            if ex.code in BUSY_CODES:
                raise AnalyzerBusyError(f"Gemini is busy right now (it answered {ex.code})") from ex
            raise AnalyzerError(f"Gemini answered {ex.code}: {ex.message}") from ex
        return parse_summary(response.parsed, response.text)


def parse_summary(parsed: object, text: str | None) -> RawSummary:
    """The parsed answer, or the JSON text read again if the SDK could not parse it."""
    if isinstance(parsed, RawSummary):
        return parsed
    try:
        return RawSummary.model_validate_json(text or "")
    except ValidationError as ex:
        raise AnalyzerError("The answer of the model is not valid JSON") from ex
