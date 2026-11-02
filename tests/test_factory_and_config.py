import os

from app import config
from app.analyzers import factory
from app.analyzers.fake import FakeAnalyzer
from app.analyzers.fallback import FallbackAnalyzer
from app.analyzers.gemini import GeminiAnalyzer
from app.analyzers.retrying import RetryingAnalyzer


def reload(monkeypatch, **env):
    for key in ("ANALYZER", "GEMINI_API_KEY", "GEMINI_MODEL", "SERVICE_TOKEN", "MAX_FILE_MB",
                "GEMINI_FALLBACK_MODEL", "GEMINI_RETRIES", "MAX_PDF_PAGES"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(config, "_load_dotenv", lambda: None)
    config.get_settings.cache_clear()
    factory.get_analyzer.cache_clear()


def test_defaults(monkeypatch):
    reload(monkeypatch)
    settings = config.get_settings()
    assert settings.analyzer == "gemini"
    assert settings.gemini_model == config.DEFAULT_MODEL
    assert settings.max_file_mb == 10
    assert settings.service_token == ""
    assert settings.gemini_fallback_model == config.DEFAULT_FALLBACK_MODEL
    assert settings.gemini_retries == 2
    assert settings.max_pdf_pages == 10


def test_reads_environment(monkeypatch):
    reload(monkeypatch, ANALYZER=" Fake ", GEMINI_MODEL="other-model", MAX_FILE_MB="5", SERVICE_TOKEN="abc")
    settings = config.get_settings()
    assert settings.analyzer == "fake"
    assert settings.gemini_model == "other-model"
    assert settings.max_file_mb == 5
    assert settings.service_token == "abc"


def test_reads_the_fallback_model_and_retries(monkeypatch):
    reload(monkeypatch, GEMINI_FALLBACK_MODEL=" backup-model ", GEMINI_RETRIES="3")
    settings = config.get_settings()
    assert settings.gemini_fallback_model == "backup-model"
    assert settings.gemini_retries == 3


def test_empty_fallback_and_negative_retries(monkeypatch):
    reload(monkeypatch, GEMINI_FALLBACK_MODEL="", GEMINI_RETRIES="-1")
    settings = config.get_settings()
    assert settings.gemini_fallback_model == ""
    assert settings.gemini_retries == 0


def test_factory_picks_fake(monkeypatch):
    reload(monkeypatch, ANALYZER="fake")
    assert isinstance(factory.get_analyzer(), FakeAnalyzer)


def test_factory_picks_gemini_by_default(monkeypatch):
    reload(monkeypatch, GEMINI_API_KEY="key")
    analyzer = factory.get_analyzer()
    assert isinstance(analyzer, FallbackAnalyzer)
    assert isinstance(analyzer.main.inner, GeminiAnalyzer)
    assert analyzer.model_name == config.DEFAULT_MODEL
    assert analyzer.ready()


def test_dotenv_does_not_override_real_variables(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nMAX_FILE_MB=3\nGEMINI_MODEL=from-file\n\nBROKEN LINE\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_MODEL", "from-env")
    monkeypatch.delenv("MAX_FILE_MB", raising=False)
    config._load_dotenv(env_file)
    assert os.environ["GEMINI_MODEL"] == "from-env"
    assert os.environ["MAX_FILE_MB"] == "3"
    monkeypatch.delenv("MAX_FILE_MB")


def test_factory_passes_the_fallback_model_and_retries(monkeypatch):
    reload(monkeypatch, GEMINI_API_KEY="key", GEMINI_FALLBACK_MODEL="backup-model", GEMINI_RETRIES="1")
    analyzer = factory.get_analyzer()
    assert analyzer.backup.model_name == "backup-model"
    assert analyzer.main.retries == 1
    assert analyzer.backup.retries == 1


def test_reads_the_pdf_page_limit(monkeypatch):
    reload(monkeypatch, MAX_PDF_PAGES="4")
    assert config.get_settings().max_pdf_pages == 4


def test_pdf_page_limit_is_at_least_one(monkeypatch):
    reload(monkeypatch, MAX_PDF_PAGES="0")
    assert config.get_settings().max_pdf_pages == 1


def test_no_backup_without_a_fallback_model(monkeypatch):
    reload(monkeypatch, GEMINI_API_KEY="key", GEMINI_FALLBACK_MODEL="")
    analyzer = factory.get_analyzer()
    assert isinstance(analyzer, RetryingAnalyzer)
    assert analyzer.inner.model_name == config.DEFAULT_MODEL


def test_no_backup_when_it_is_the_main_model(monkeypatch):
    reload(monkeypatch, GEMINI_API_KEY="key", GEMINI_MODEL="same", GEMINI_FALLBACK_MODEL="same")
    assert isinstance(factory.get_analyzer(), RetryingAnalyzer)
