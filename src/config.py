"""
Configuration loader for Jira Milestone Reporter.

Reads and validates environment variables required to run the milestone reporter.
"""

import os
from typing import Dict, Optional


class Config:
    """Loads and validates configuration from environment variables."""

    # Mandatory environment variables
    MANDATORY_VARS = [
        "JIRA_BASE_URL",
        "JIRA_USERNAME",
        "JIRA_API_TOKEN",
        "JIRA_PROJECT_KEY",
    ]

    # Optional environment variables with defaults
    DEFAULT_OUTPUT_DIR = "./output"
    DEFAULT_START_DATE_FIELD = None  # e.g., "customfield_10015"

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        self._jira_base_url: str = os.environ.get("JIRA_BASE_URL", "").strip()
        self._jira_username: str = os.environ.get("JIRA_USERNAME", "").strip()
        self._jira_api_token: str = os.environ.get("JIRA_API_TOKEN", "").strip()
        self._jira_project_key: str = os.environ.get("JIRA_PROJECT_KEY", "").strip()
        self._output_dir: str = os.environ.get(
            "OUTPUT_DIR", self.DEFAULT_OUTPUT_DIR
        ).strip()
        self._start_date_field: Optional[str] = os.environ.get(
            "START_DATE_FIELD", self.DEFAULT_START_DATE_FIELD
        )
        self._timeline_title: str = os.environ.get("TIMELINE_TITLE", "Jira Milestones Report").strip()

    @property
    def jira_base_url(self) -> str:
        """Get Jira Base URL."""
        return self._jira_base_url

    @property
    def jira_username(self) -> str:
        """Get Jira username (email)."""
        return self._jira_username

    @property
    def jira_api_token(self) -> str:
        """Get Jira API token."""
        return self._jira_api_token

    @property
    def jira_project_key(self) -> str:
        """Get Jira project key."""
        return self._jira_project_key

    @property
    def output_dir(self) -> str:
        """Get output directory path."""
        return self._output_dir

    @property
    def start_date_field(self) -> Optional[str]:
        """Get optional start date custom field ID."""
        return self._start_date_field

    @property
    def timeline_title(self) -> str:
        """Get timeline title."""
        return self._timeline_title

    def validate(self) -> None:
        """
        Validate that all mandatory variables are set.

        Raises:
            ValueError: If any mandatory variable is missing or empty.
        """
        missing_vars = []

        for var_name in self.MANDATORY_VARS:
            value = getattr(self, f"_{var_name.lower()}", "").strip()
            if not value:
                missing_vars.append(var_name)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Validate URL format
        if not self._jira_base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"JIRA_BASE_URL must start with http:// or https://, got: {self._jira_base_url}"
            )

    def to_dict(self) -> Dict[str, str]:
        """
        Get all configuration values as a dictionary.

        Sensitive values (API token) are masked for safe logging.

        Returns:
            Dictionary containing all configuration values.
        """
        return {
            "jira_base_url": self._jira_base_url,
            "jira_username": self._jira_username,
            "jira_api_token": "***" if self._jira_api_token else "",
            "jira_project_key": self._jira_project_key,
            "output_dir": self._output_dir,
            "start_date_field": self._start_date_field or "None",
            "timeline_title": self._timeline_title,
        }
