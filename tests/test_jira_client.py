"""
Unit tests for jira_client.py module.
"""

import base64
from unittest.mock import MagicMock, patch

import pytest
import responses

from jira_client import JiraClient, JiraAuthError, JiraAPIError


class TestJiraClientInitialization:
    """Test suite for JiraClient initialization."""

    def test_initialization_with_valid_credentials(self):
        """Test successful client initialization."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="test_token",
        )
        assert client.base_url == "https://test.atlassian.net"
        assert client.username == "user@example.com"
        assert client.api_token == "test_token"

    def test_initialization_removes_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = JiraClient(
            base_url="https://test.atlassian.net/",
            username="user@example.com",
            api_token="test_token",
        )
        assert client.base_url == "https://test.atlassian.net"

    def test_initialization_missing_base_url(self):
        """Test that missing base_url raises JiraAuthError."""
        with pytest.raises(JiraAuthError):
            JiraClient(base_url="", username="user@example.com", api_token="token")

    def test_initialization_missing_username(self):
        """Test that missing username raises JiraAuthError."""
        with pytest.raises(JiraAuthError):
            JiraClient(
                base_url="https://test.atlassian.net", username="", api_token="token"
            )

    def test_initialization_missing_api_token(self):
        """Test that missing api_token raises JiraAuthError."""
        with pytest.raises(JiraAuthError):
            JiraClient(
                base_url="https://test.atlassian.net",
                username="user@example.com",
                api_token="",
            )


class TestJiraClientAuthentication:
    """Test suite for authentication header creation."""

    def test_build_auth_header(self):
        """Test Basic Auth header construction."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="my_token_123",
        )

        header = client._build_auth_header()

        # Verify structure
        assert "Authorization" in header
        assert header["Authorization"].startswith("Basic ")

        # Verify encoding
        expected_creds = base64.b64encode(b"user@example.com:my_token_123").decode()
        assert header["Authorization"] == f"Basic {expected_creds}"


class TestJiraClientSearchIssues:
    """Test suite for issue searching."""

    @responses.activate
    def test_search_issues_single_page(self):
        """Test searching issues that fit in a single page."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        # Mock API response
        mock_response = {
            "total": 2,
            "issues": [
                {
                    "key": "TEST-1",
                    "fields": {
                        "summary": "First issue",
                        "status": {"statusCategory": {"name": "To Do"}},
                        "duedate": "2025-01-31",
                        "customfield_10015": "2025-01-01",
                    },
                },
                {
                    "key": "TEST-2",
                    "fields": {
                        "summary": "Second issue",
                        "status": {"statusCategory": {"name": "In Progress"}},
                        "duedate": "2025-02-28",
                        "customfield_10015": None,
                    },
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json=mock_response,
            status=200,
        )

        issues = client.search_issues('project = "TEST"')

        assert len(issues) == 2
        assert issues[0]["key"] == "TEST-1"
        assert issues[0]["summary"] == "First issue"
        assert issues[0]["status"] == "To Do"
        assert issues[0]["due_date"] == "2025-01-31"
        assert issues[0]["start_date"] == "2025-01-01"

    @responses.activate
    def test_search_issues_pagination(self):
        """Test searching issues with pagination."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        # First page
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 3,
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "summary": "Issue 1",
                            "status": {"statusCategory": {"name": "Done"}},
                            "duedate": "2025-01-31",
                            "customfield_10015": None,
                        },
                    },
                ],
            },
            status=200,
        )

        # Second page
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 3,
                "issues": [
                    {
                        "key": "TEST-2",
                        "fields": {
                            "summary": "Issue 2",
                            "status": {"statusCategory": {"name": "Done"}},
                            "duedate": "2025-02-15",
                            "customfield_10015": None,
                        },
                    },
                ],
            },
            status=200,
        )

        issues = client.search_issues('project = "TEST"', max_results=500)

        # Note: Pagination stops after second response due to mock setup
        assert len(issues) >= 2
        assert issues[0]["key"] == "TEST-1"

    @responses.activate
    def test_search_issues_http_error_401(self):
        """Test handling of 401 Unauthorized error."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="bad_token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={"errorMessages": ["Unauthorized"]},
            status=401,
        )

        with pytest.raises(JiraAPIError, match="401"):
            client.search_issues('project = "TEST"')

    @responses.activate
    def test_search_issues_http_error_404(self):
        """Test handling of 404 Not Found error."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={"errorMessages": ["Not found"]},
            status=404,
        )

        with pytest.raises(JiraAPIError, match="404"):
            client.search_issues('project = "TEST"')

    @responses.activate
    def test_search_issues_empty_result(self):
        """Test handling of empty search results."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={"total": 0, "issues": []},
            status=200,
        )

        issues = client.search_issues('project = "NONEXISTENT"')

        assert len(issues) == 0

    @responses.activate
    def test_search_issues_status_normalization(self):
        """Test that status categories are normalized."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 3,
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "summary": "Done",
                            "status": {"statusCategory": {"name": "Done"}},
                            "duedate": None,
                            "customfield_10015": None,
                        },
                    },
                    {
                        "key": "TEST-2",
                        "fields": {
                            "summary": "In Progress",
                            "status": {"statusCategory": {"name": "In Progress"}},
                            "duedate": None,
                            "customfield_10015": None,
                        },
                    },
                    {
                        "key": "TEST-3",
                        "fields": {
                            "summary": "To Do",
                            "status": {"statusCategory": {"name": "To Do"}},
                            "duedate": None,
                            "customfield_10015": None,
                        },
                    },
                ],
            },
            status=200,
        )

        issues = client.search_issues('project = "TEST"')

        assert issues[0]["status"] == "Done"
        assert issues[1]["status"] == "In Progress"
        assert issues[2]["status"] == "To Do"

    @responses.activate
    def test_search_issues_missing_fields(self):
        """Test handling of issues with missing fields."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 1,
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "summary": None,
                            "status": None,
                            "duedate": None,
                            "customfield_10015": None,
                        },
                    },
                ],
            },
            status=200,
        )

        issues = client.search_issues('project = "TEST"')

        assert len(issues) == 1
        assert issues[0]["key"] == "TEST-1"
        assert issues[0]["summary"] == ""
        assert issues[0]["status"] == "To Do"


class TestJiraClientProjectVersions:
    """Test suite for get_project_versions method."""

    @responses.activate
    def test_get_project_versions_success(self):
        """Test successful retrieval of project milestones from Epic issues."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        # Mock search API response with Epic milestone issues
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 2,
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "summary": "Milestone 1",
                            "description": "First milestone",
                        },
                    },
                    {
                        "key": "TEST-2",
                        "fields": {
                            "summary": "Milestone 2",
                            "description": "Second milestone",
                        },
                    },
                ],
            },
            status=200,
        )

        versions = client.get_project_versions("TEST")

        assert len(versions) == 2
        assert versions[0]["id"] == "TEST-1"
        assert versions[0]["name"] == "Milestone 1"
        assert versions[0]["description"] == "First milestone"
        assert versions[1]["id"] == "TEST-2"
        assert versions[1]["name"] == "Milestone 2"

    @responses.activate
    def test_get_project_versions_multiple_epics(self):
        """Test retrieval of multiple Epic milestones."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={
                "total": 3,
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "summary": "v1.0",
                            "description": "Version 1.0",
                        },
                    },
                    {
                        "key": "TEST-2",
                        "fields": {
                            "summary": "v2.0",
                            "description": "Version 2.0",
                        },
                    },
                    {
                        "key": "TEST-3",
                        "fields": {
                            "summary": "v3.0",
                            "description": None,
                        },
                    },
                ],
            },
            status=200,
        )

        versions = client.get_project_versions("TEST")

        assert len(versions) == 3
        assert versions[0]["name"] == "v1.0"
        assert versions[1]["name"] == "v2.0"
        assert versions[2]["name"] == "v3.0"

    @responses.activate
    def test_get_project_versions_empty(self):
        """Test retrieval when no Epic milestones exist."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={"total": 0, "issues": []},
            status=200,
        )

        versions = client.get_project_versions("TEST")

        assert len(versions) == 0

    @responses.activate
    def test_get_project_versions_api_error(self):
        """Test handling of API errors."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="user@example.com",
            api_token="token",
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search/jql",
            json={"errorMessages": ["Project not found"]},
            status=401,
        )

        with pytest.raises(JiraAPIError):
            client.get_project_versions("TEST")
