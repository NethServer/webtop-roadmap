"""Unit tests for config.py module."""

import os
import pytest

from config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_successful_loading_with_all_variables(self, monkeypatch):
        """Test successful configuration loading with all required variables."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token_12345",
            "JIRA_PROJECT_KEY": "TEST",
            "OUTPUT_DIR": "./output",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        assert config.jira_base_url == "https://test.atlassian.net"
        assert config.jira_username == "user@example.com"
        assert config.jira_api_token == "test_token_12345"
        assert config.jira_project_key == "TEST"
        assert config.output_dir == "./output"
        assert config.timeline_title == "Test Timeline"

    def test_default_output_dir(self, monkeypatch):
        """Test that default output directory is used when not provided."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("OUTPUT_DIR", raising=False)

        config = Config()
        assert config.output_dir == "./output"

    def test_missing_jira_base_url(self, monkeypatch):
        """Test validation fails when JIRA_BASE_URL is missing."""
        env_vars = {
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("JIRA_BASE_URL", raising=False)

        config = Config()
        with pytest.raises(ValueError, match="Missing required environment variables"):
            config.validate()

    def test_missing_jira_username(self, monkeypatch):
        """Test validation fails when JIRA_USERNAME is missing."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("JIRA_USERNAME", raising=False)

        config = Config()
        with pytest.raises(ValueError, match="Missing required environment variables"):
            config.validate()

    def test_missing_jira_api_token(self, monkeypatch):
        """Test validation fails when JIRA_API_TOKEN is missing."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        config = Config()
        with pytest.raises(ValueError, match="Missing required environment variables"):
            config.validate()

    def test_missing_jira_project_key(self, monkeypatch):
        """Test validation fails when JIRA_PROJECT_KEY is missing."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("JIRA_PROJECT_KEY", raising=False)

        config = Config()
        with pytest.raises(ValueError, match="Missing required environment variables"):
            config.validate()

    def test_timeline_title_optional(self, monkeypatch):
        """Test that TIMELINE_TITLE is optional with default value."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("TIMELINE_TITLE", raising=False)

        config = Config()
        config.validate()  # Should not raise
        assert config.timeline_title == "Jira Milestones Report"

    def test_invalid_url_format(self, monkeypatch):
        """Test validation fails with invalid URL format."""
        env_vars = {
            "JIRA_BASE_URL": "not-a-url",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        with pytest.raises(ValueError, match="JIRA_BASE_URL must start with"):
            config.validate()

    def test_valid_http_url(self, monkeypatch):
        """Test that HTTP URLs are accepted."""
        env_vars = {
            "JIRA_BASE_URL": "http://test.example.com",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        config.validate()  # Should not raise
        assert config.jira_base_url == "http://test.example.com"

    def test_to_dict_masks_api_token(self, monkeypatch):
        """Test that to_dict() masks the API token."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "secret_token_12345",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        config_dict = config.to_dict()

        assert config_dict["jira_api_token"] == "***"
        assert config_dict["jira_username"] == "user@example.com"

    def test_to_dict_with_empty_token(self, monkeypatch):
        """Test that to_dict() handles missing token gracefully."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        config = Config()
        config_dict = config.to_dict()

        assert config_dict["jira_api_token"] == ""

    def test_whitespace_trimming(self, monkeypatch):
        """Test that leading/trailing whitespace is trimmed."""
        env_vars = {
            "JIRA_BASE_URL": "  https://test.atlassian.net  ",
            "JIRA_USERNAME": "  user@example.com  ",
            "JIRA_API_TOKEN": "  test_token  ",
            "JIRA_PROJECT_KEY": "  TEST  ",
            "TIMELINE_TITLE": "  Test Timeline  ",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        assert config.jira_base_url == "https://test.atlassian.net"
        assert config.jira_username == "user@example.com"
        assert config.jira_api_token == "test_token"
        assert config.jira_project_key == "TEST"
        assert config.timeline_title == "Test Timeline"

    def test_validate_success(self, monkeypatch):
        """Test that validate() returns None on success."""
        env_vars = {
            "JIRA_BASE_URL": "https://test.atlassian.net",
            "JIRA_USERNAME": "user@example.com",
            "JIRA_API_TOKEN": "test_token",
            "JIRA_PROJECT_KEY": "TEST",
            "TIMELINE_TITLE": "Test Timeline",
        }
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        config = Config()
        result = config.validate()
        assert result is None
