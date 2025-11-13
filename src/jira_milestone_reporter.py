#!/usr/bin/env python3
"""Jira Milestone Reporter.

Generates HTML reports for all open milestones in a Jira project.

This script:
1. Loads configuration from environment variables
2. Fetches all project versions (milestones) from Jira
3. Filters to open milestones (not released, not archived)
4. For each milestone, fetches all issues and generates HTML report
5. Creates index.html with links to all milestone reports

Usage:
    python jira_milestone_reporter.py

Environment Variables:
    JIRA_BASE_URL: Jira instance URL (required)
    JIRA_USERNAME: Jira username/email (required)
    JIRA_API_TOKEN: Jira API token (required)
    JIRA_PROJECT_KEY: Jira project key (required)
    OUTPUT_DIR: Output directory (optional, default: ./output)
    TIMELINE_TITLE: Report title (required)
    START_DATE_FIELD: Custom start date field (optional)
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on sys.path so `from src.*` works when running
# `python src/jira_milestone_reporter.py` directly.
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import Config
from src.jira_client import JiraClient, JiraClientError
from src.html_renderer import HTMLRenderer


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure logging for the application.

    Args:
        level: Logging level (default: INFO)

    Returns:
        Logger instance
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load .env file
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    logger = setup_logging()

    try:
        # Phase 1: Setup
        logger.info("=" * 70)
        logger.info("Jira Milestone Reporter")
        logger.info("=" * 70)

        logger.info("Phase 1: Loading configuration...")
        config = Config()
        config.validate()
        logger.debug(f"Configuration: {config.to_dict()}")

        output_dir = Path(config.output_dir)
        client = JiraClient(
            config.jira_base_url, config.jira_username, config.jira_api_token
        )
        renderer = HTMLRenderer(config.jira_base_url, config.timeline_title)
        logger.info("✓ Configuration and client initialized")

        # Phase 2: Fetch all project versions
        logger.info("Phase 2: Fetching project versions...")
        try:
            versions = client.get_project_versions(config.jira_project_key)
            logger.info(f"Retrieved {len(versions)} versions from project")
        except JiraClientError as e:
            logger.error(f"Failed to fetch versions: {e}")
            return 1

        # Phase 3: Filter to open milestones
        logger.info("Phase 3: Filtering open milestones...")
        open_milestones = [
            v for v in versions if not v.get("released") and not v.get("archived")
        ]
        logger.info(f"Found {len(open_milestones)} open milestones")

        if not open_milestones:
            logger.warning("No open milestones found")
            return 0

        # Phase 4: Generate milestone reports
        logger.info("Phase 4: Generating milestone reports...")
        milestones_with_issues = []

        for milestone in open_milestones:
            milestone_name = milestone.get("name", "Unknown")
            milestone_key = milestone.get("key", "")
            logger.info(f"  Processing milestone: {milestone_name} ({milestone_key})")

            try:
                # Fetch issues linked to this Epic milestone
                jql = (
                    f'project = "{config.jira_project_key}" '
                    f'AND "Epic Link" = {milestone_key}'
                )
                issues = client.search_issues(jql)
                logger.debug(f"    Retrieved {len(issues)} issues")

                # Skip milestones with no issues
                if not issues:
                    logger.info(f"    Skipping milestone {milestone_name} (0 issues)")
                    continue

                # Prepare issue data
                formatted_issues = [
                    {
                        "key": issue.get("key"),
                        "summary": issue.get("summary"),
                        "status": issue.get("status"),
                        "due_date": issue.get("due_date", ""),
                        "start_date": issue.get("start_date", ""),
                        "assignee": issue.get("assignee", "Unassigned"),
                    }
                    for issue in issues
                ]

                # Generate HTML report for this milestone
                renderer.render_milestone_report(milestone, formatted_issues, output_dir)
                logger.info(f"    ✓ Generated report for {milestone_name}")

                # Track milestone for index
                milestones_with_issues.append(
                    {
                        "id": milestone.get("id"),
                        "name": milestone_name,
                        "description": milestone.get("description", ""),
                        "issue_count": len(formatted_issues),
                    }
                )

            except JiraClientError as e:
                logger.error(f"  Failed to fetch issues for {milestone_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"  Failed to generate report for {milestone_name}: {e}")
                continue

        # Phase 5: Generate index
        logger.info("Phase 5: Generating index.html...")
        try:
            renderer.render_index(milestones_with_issues, output_dir)
            logger.info("✓ Generated index.html")
        except Exception as e:
            logger.error(f"Failed to generate index: {e}")
            return 1

        logger.info("=" * 70)
        logger.info(f"✓ Success! Reports generated in: {output_dir.resolve()}")
        logger.info("=" * 70)
        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
