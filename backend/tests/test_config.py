from performance_cockpit.config import Settings


def test_settings_use_safe_development_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.cors_origins == ["http://localhost:5173"]
