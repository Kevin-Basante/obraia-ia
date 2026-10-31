import os

from app import config


def reload(monkeypatch, **env):
    for key in ("ANALYZER", "GEMINI_API_KEY", "GEMINI_MODEL", "SERVICE_TOKEN", "MAX_FILE_MB"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(config, "_load_dotenv", lambda: None)
    config.get_settings.cache_clear()


def test_defaults(monkeypatch):
    reload(monkeypatch)
    settings = config.get_settings()
    assert settings.analyzer == "gemini"
    assert settings.gemini_model == config.DEFAULT_MODEL
    assert settings.max_file_mb == 10
    assert settings.service_token == ""


def test_reads_environment(monkeypatch):
    reload(monkeypatch, ANALYZER=" Fake ", GEMINI_MODEL="other-model", MAX_FILE_MB="5", SERVICE_TOKEN="abc")
    settings = config.get_settings()
    assert settings.analyzer == "fake"
    assert settings.gemini_model == "other-model"
    assert settings.max_file_mb == 5
    assert settings.service_token == "abc"


def test_dotenv_does_not_override_real_variables(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nMAX_FILE_MB=3\nGEMINI_MODEL=from-file\n\nBROKEN LINE\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_MODEL", "from-env")
    monkeypatch.delenv("MAX_FILE_MB", raising=False)
    config._load_dotenv(env_file)
    assert os.environ["GEMINI_MODEL"] == "from-env"
    assert os.environ["MAX_FILE_MB"] == "3"
    monkeypatch.delenv("MAX_FILE_MB")
