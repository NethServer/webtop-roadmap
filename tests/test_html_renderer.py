"""Unit tests for html_renderer.py module."""

import pytest
from pathlib import Path
from html_renderer import HTMLRenderer


class TestHTMLRendererInitialization:
    """Test suite for HTMLRenderer initialization."""

    def test_initialization(self):
        """Test successful renderer initialization."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test Timeline"
        )
        assert renderer.base_url == "https://test.atlassian.net"
        assert renderer.title == "Test Timeline"

    def test_initialization_removes_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net/", title="Test"
        )
        assert renderer.base_url == "https://test.atlassian.net"


class TestHTMLRendererSlugify:
    """Test suite for _slugify method."""

    def test_slugify_lowercase(self):
        """Test that slugify converts to lowercase."""
        renderer = HTMLRenderer(base_url="https://test.atlassian.net", title="Test")
        assert renderer._slugify("TEST") == "test"
        assert renderer._slugify("Test Milestone") == "test_milestone"

    def test_slugify_spaces_to_underscores(self):
        """Test that spaces are converted to underscores."""
        renderer = HTMLRenderer(base_url="https://test.atlassian.net", title="Test")
        assert renderer._slugify("My Milestone") == "my_milestone"
        assert renderer._slugify("Release 1.0") == "release_1.0"

    def test_slugify_slashes_to_dashes(self):
        """Test that slashes are converted to dashes."""
        renderer = HTMLRenderer(base_url="https://test.atlassian.net", title="Test")
        assert renderer._slugify("Q1/2025") == "q1-2025"


class TestHTMLRendererIssueUrl:
    """Test suite for _get_issue_url method."""

    def test_issue_url_generation(self):
        """Test that issue URLs are generated correctly."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        url = renderer._get_issue_url("TEST-123")
        assert url == "https://test.atlassian.net/browse/TEST-123"

    def test_issue_url_with_multiple_project_keys(self):
        """Test issue URL generation with different keys."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        assert (
            renderer._get_issue_url("PROJ-1")
            == "https://test.atlassian.net/browse/PROJ-1"
        )
        assert (
            renderer._get_issue_url("ANOTHER-999")
            == "https://test.atlassian.net/browse/ANOTHER-999"
        )


class TestHTMLRendererIndex:
    """Test suite for render_index method."""

    def test_render_index_creates_file(self, tmp_path):
        """Test that render_index creates index.html."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestones = [
            {"name": "v1.0", "description": "Initial release", "issue_count": 10},
            {"name": "v2.0", "description": "Major update", "issue_count": 15},
        ]

        output_path = renderer.render_index(milestones, tmp_path)

        assert output_path.exists()
        assert output_path.name == "index.html"

    def test_render_index_html_structure(self, tmp_path):
        """Test that index.html has correct structure."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="My Milestones"
        )
        milestones = [
            {"name": "v1.0", "description": "Release 1", "issue_count": 5}
        ]

        renderer.render_index(milestones, tmp_path)
        index_file = tmp_path / "index.html"

        content = index_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "My Milestones" in content
        assert "v1.0" in content
        assert "Release 1" in content

    def test_render_index_with_empty_milestones(self, tmp_path):
        """Test render_index with no milestones."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestones = []

        renderer.render_index(milestones, tmp_path)
        index_file = tmp_path / "index.html"

        assert index_file.exists()


class TestHTMLRendererMilestoneReport:
    """Test suite for render_milestone_report method."""

    def test_render_milestone_creates_file(self, tmp_path):
        """Test that render_milestone_report creates milestone file."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestone = {"name": "v1.0", "description": "Release 1"}
        issues = [
            {
                "key": "TEST-1",
                "summary": "Implement feature",
                "status": "In Progress",
                "due_date": "2025-01-31",
                "start_date": "2025-01-01",
                "assignee": "John Doe",
            }
        ]

        output_path = renderer.render_milestone_report(milestone, issues, tmp_path)

        assert output_path.exists()
        assert output_path.name == "milestone-v1.0.html"

    def test_render_milestone_html_structure(self, tmp_path):
        """Test that milestone HTML has correct structure."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="My Project"
        )
        milestone = {"name": "v1.0", "description": "Version 1.0"}
        issues = [
            {
                "key": "TEST-1",
                "summary": "Task 1",
                "status": "Done",
                "due_date": "2025-01-31",
                "start_date": "2025-01-01",
                "assignee": "Jane",
            }
        ]

        renderer.render_milestone_report(milestone, issues, tmp_path)
        milestone_file = tmp_path / "milestone-v1.0.html"

        content = milestone_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "v1.0" in content
        assert "TEST-1" in content
        assert "Task 1" in content

    def test_render_milestone_with_no_issues(self, tmp_path):
        """Test render_milestone_report with no issues."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestone = {"name": "empty", "description": "Empty milestone"}
        issues = []

        renderer.render_milestone_report(milestone, issues, tmp_path)
        milestone_file = tmp_path / "milestone-empty.html"

        content = milestone_file.read_text()
        assert "No issues found" in content

    def test_render_milestone_status_badges(self, tmp_path):
        """Test that status badges are correctly colored."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestone = {"name": "test", "description": "Test"}
        issues = [
            {
                "key": "TEST-1",
                "summary": "Done task",
                "status": "Done",
                "due_date": "",
                "start_date": "",
                "assignee": "User",
            },
            {
                "key": "TEST-2",
                "summary": "In progress",
                "status": "In Progress",
                "due_date": "",
                "start_date": "",
                "assignee": "User",
            },
            {
                "key": "TEST-3",
                "summary": "Todo",
                "status": "To Do",
                "due_date": "",
                "start_date": "",
                "assignee": "User",
            },
        ]

        renderer.render_milestone_report(milestone, issues, tmp_path)
        milestone_file = tmp_path / "milestone-test.html"

        content = milestone_file.read_text()
        assert "status-green" in content  # Done
        assert "status-orange" in content  # In Progress
        assert "status-gray" in content  # To Do

    def test_render_milestone_issue_links(self, tmp_path):
        """Test that issue keys are linked to Jira."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Test"
        )
        milestone = {"name": "test", "description": "Test"}
        issues = [
            {
                "key": "PROJ-42",
                "summary": "Issue summary",
                "status": "Done",
                "due_date": "",
                "start_date": "",
                "assignee": "User",
            }
        ]

        renderer.render_milestone_report(milestone, issues, tmp_path)
        milestone_file = tmp_path / "milestone-test.html"

        content = milestone_file.read_text()
        assert "https://test.atlassian.net/browse/PROJ-42" in content
        assert 'target="_blank"' in content


class TestHTMLRendererIntegration:
    """Integration tests for HTML rendering."""

    def test_complete_workflow(self, tmp_path):
        """Test complete workflow of generating both index and milestone reports."""
        renderer = HTMLRenderer(
            base_url="https://test.atlassian.net", title="Project Roadmap"
        )

        # Render index
        milestones = [
            {
                "name": "v1.0",
                "description": "Initial release",
                "issue_count": 5,
            }
        ]
        index_path = renderer.render_index(milestones, tmp_path)

        # Render milestone report
        milestone_data = {"name": "v1.0", "description": "Initial release"}
        issues = [
            {
                "key": "TEST-1",
                "summary": "Feature",
                "status": "Done",
                "due_date": "2025-01-31",
                "start_date": "2025-01-01",
                "assignee": "Developer",
            }
        ]
        milestone_path = renderer.render_milestone_report(
            milestone_data, issues, tmp_path
        )

        # Verify both files exist
        assert index_path.exists()
        assert milestone_path.exists()

        # Verify index references milestone
        index_content = index_path.read_text()
        assert "milestone-v1.0.html" in index_content
