"""
Jira API client for fetching issues from Jira Cloud.

Handles authentication, API calls, pagination, and error handling.
"""

import base64
import logging
import time
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class JiraClientError(Exception):
    """Base exception for Jira client errors."""

    pass


class JiraAuthError(JiraClientError):
    """Authentication error with Jira API."""

    pass


class JiraAPIError(JiraClientError):
    """Jira API error response."""

    pass


class JiraClient:
    """Client for interacting with Jira Cloud REST API."""

    # Jira API version and endpoints
    API_VERSION = "3"
    SEARCH_ENDPOINT = "/rest/api/{version}/search/jql"

        # Fields to retrieve from Jira
    FIELDS = [
        "key",
        "summary",
        "status",
        "duedate",
        "assignee",
        "customfield_10015",  # Start date (common custom field)
        "customfield_10037",  # Fix Version (milestone)
        "customfield_10041",  # Affects Version (milestone)
    ]

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 0.5
    TIMEOUT_SECONDS = 30

    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize Jira client.

        Args:
            base_url: Base URL of Jira instance (e.g., https://domain.atlassian.net)
            username: Jira username (email address)
            api_token: Jira API token

        Raises:
            JiraAuthError: If credentials are invalid or missing
        """
        if not all([base_url, username, api_token]):
            raise JiraAuthError("Base URL, username, and API token are required")

        self.base_url = base_url.rstrip("/")
        self.username = username
        self.api_token = api_token

        # Setup session with retry strategy
        self.session = self._setup_session()

    def _setup_session(self) -> requests.Session:
        """
        Set up requests session with retry strategy.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _build_auth_header(self) -> Dict[str, str]:
        """
        Build Basic Auth header for Jira API.

        Returns:
            Dictionary with Authorization header
        """
        credentials = f"{self.username}:{self.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> Dict:
        """
        Make an HTTP request to Jira API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative path)
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            JiraAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_auth_header()
        headers["Accept"] = "application/json"

        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                timeout=self.TIMEOUT_SECONDS,
            )

            # Check for HTTP errors
            if response.status_code >= 400:
                error_body = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("errorMessages", [error_body])
                    if isinstance(error_msg, list):
                        error_msg = "; ".join(error_msg)
                except Exception:
                    error_msg = error_body

                raise JiraAPIError(
                    f"Jira API error ({response.status_code}): {error_msg}"
                )

            return response.json()

        except requests.RequestException as e:
            raise JiraAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise JiraAPIError(f"Invalid JSON response: {str(e)}")

    def _normalize_issue(self, issue: Dict) -> Dict:
        """
        Normalize Jira issue to standard format.

        Args:
            issue: Raw Jira issue JSON

        Returns:
            Normalized issue dictionary
        """
        fields = issue.get("fields", {})

        # Extract status category
        status_obj = fields.get("status", {})
        status_category = (
            status_obj.get("statusCategory", {}).get("name", "To Do")
            if status_obj
            else "To Do"
        )

        # Normalize status category name
        status_map = {
            "Done": "Done",
            "In Progress": "In Progress",
            "To Do": "To Do",
        }
        normalized_status = status_map.get(status_category, status_category)
        
        # Extract milestone from customfield_10037 or customfield_10041
        milestone = ""
        fix_version = fields.get("customfield_10037")
        if fix_version:
            if isinstance(fix_version, list) and fix_version:
                milestone = fix_version[0].get("name", "") if isinstance(fix_version[0], dict) else str(fix_version[0])
            elif isinstance(fix_version, dict):
                milestone = fix_version.get("name", "")
            else:
                milestone = str(fix_version)
        
        # Fallback to affects version if fix version not set
        if not milestone:
            affects_version = fields.get("customfield_10041")
            if affects_version:
                if isinstance(affects_version, list) and affects_version:
                    milestone = affects_version[0].get("name", "") if isinstance(affects_version[0], dict) else str(affects_version[0])
                elif isinstance(affects_version, dict):
                    milestone = affects_version.get("name", "")
                else:
                    milestone = str(affects_version)

        # Extract assignee
        assignee_obj = fields.get("assignee")
        assignee = assignee_obj.get("displayName") if assignee_obj else "Unassigned"

        return {
            "key": issue.get("key", ""),
            "summary": fields.get("summary") or "",
            "status": normalized_status,
            "due_date": fields.get("duedate"),
            "start_date": fields.get("customfield_10015"),
            "milestone": milestone,
            "assignee": assignee,
        }

    def search_issues(
        self,
        jql: str,
        max_results: int = 500,
    ) -> List[Dict]:
        """
        Search for issues using JQL query.

        Args:
            jql: JQL query string
            max_results: Maximum number of results to return

        Returns:
            List of normalized issue dictionaries

        Raises:
            JiraAPIError: If search fails
        """
        all_issues = []
        start_at = 0

        logger.info(f"Starting issue search with JQL: {jql}")

        while True:
            # Note: Using /rest/api/3/search/jql endpoint (new API)
            params = {
                "jql": jql,
                "fields": ",".join(self.FIELDS),
                "maxResults": min(50, max_results - len(all_issues)),
                "startAt": start_at,
            }

            try:
                endpoint = self.SEARCH_ENDPOINT.format(version=self.API_VERSION)
                response = self._make_request("GET", endpoint, params=params)

                issues = response.get("issues", [])

                if not issues:
                    break

                # Normalize and add issues
                for issue in issues:
                    normalized = self._normalize_issue(issue)
                    all_issues.append(normalized)
                    logger.debug(f"Retrieved issue: {normalized['key']}")

                # Check if we have all results
                total = response.get("total", 0)
                if len(all_issues) >= total or len(all_issues) >= max_results:
                    break

                start_at += len(issues)

            except JiraAPIError as e:
                logger.error(f"Error during issue search: {e}")
                raise

        logger.info(f"Retrieved {len(all_issues)} issues")
        return all_issues

    def get_project_versions(self, project_key: str) -> List[Dict]:
        """
        Fetch all Epic issues as milestones for a project.
        
        In this project, milestones are represented as Epic issues (e.g., WT-1421 "Milestone 2").

        Args:
            project_key: Jira project key

        Returns:
            List of milestone dictionaries with id, name, description

        Raises:
            JiraAPIError: If request fails
        """
        logger.info(f"Fetching milestones (Epic issues) for project: {project_key}")

        try:
            # Search for all open Epic issues
            params = {
                "jql": f'project = "{project_key}" AND type = Epic AND statusCategory != "Done"',
                "fields": "key,summary,description",
                "maxResults": 500,
            }
            
            endpoint = self.SEARCH_ENDPOINT.format(version=self.API_VERSION)
            response = self._make_request("GET", endpoint, params=params)
            
            issues = response.get("issues", [])
            
            # Convert Epic issues to milestone format
            milestones = []
            for issue in issues:
                key = issue.get("key", "")
                fields = issue.get("fields", {})
                summary = fields.get("summary", "")
                description = fields.get("description", "")
                
                # Extract description text if it's a structured object
                if isinstance(description, dict):
                    content = description.get("content", [])
                    desc_text = ""
                    for item in content:
                        if item.get("type") == "paragraph":
                            text_items = item.get("content", [])
                            for text in text_items:
                                if text.get("type") == "text":
                                    desc_text += text.get("text", "")
                    description = desc_text
                
                milestones.append({
                    "id": key,
                    "name": summary,
                    "description": description or "",
                    "released": False,
                    "archived": False,
                    "key": key,  # Add the issue key for linking
                })
            
            logger.info(f"Retrieved {len(milestones)} milestones (Epic issues) for project {project_key}")
            return milestones

        except JiraAPIError as e:
            logger.error(f"Error fetching milestones: {e}")
            raise
