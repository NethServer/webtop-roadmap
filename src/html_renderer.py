"""HTML renderer for Jira Milestone Reporter.

Generates self-contained HTML pages:
- index.html: List of all open milestones with links
- milestone-*.html: Detailed issue table for each milestone
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Generates static HTML for milestone reports."""

    def __init__(self, base_url: str, title: str):
        """Initialize HTML renderer.

        Args:
            base_url: Jira base URL (for creating issue links)
            title: Report title
        """
        self.base_url = base_url.rstrip("/")
        self.title = title

    def _slugify(self, text: str) -> str:
        """Convert text to filesystem-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified string safe for use in filenames
        """
        return text.lower().replace(" ", "_").replace("/", "-")

    def _get_issue_url(self, issue_key: str) -> str:
        """Get full Jira URL for an issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            Full URL to the issue in Jira
        """
        return f"{self.base_url}/browse/{issue_key}"

    def render_index(self, milestones: List[Dict], output_dir: Path) -> Path:
        """Generate index.html with all open milestones.

        Args:
            milestones: List of milestone dictionaries
            output_dir: Output directory path

        Returns:
            Path to generated index.html
        """
        logger.info("Rendering index.html")

        # Create output dir if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build milestone cards HTML
        milestone_cards = []
        for milestone in milestones:
            milestone_id = milestone.get("id", "unknown")
            milestone_file = f"milestone-{milestone_id}.html"
            issue_count = milestone.get("issue_count", 0)

            card_html = (
                f'        <div class="milestone-card">\n'
                f'            <h3>{milestone.get("name", "Unknown")}</h3>\n'
                f'            <p class="milestone-description">'
                f'{milestone.get("description", "")}</p>\n'
                f'            <div class="milestone-meta">\n'
                f'                <span class="issue-count">Issues: {issue_count}</span>\n'
                f'            </div>\n'
                f'            <a href="{milestone_file}" class="milestone-link">'
                f'View Details</a>\n'
                f'        </div>'
            )
            milestone_cards.append(card_html)

        milestone_html = "\n".join(milestone_cards)

        # Generate HTML
        html_content = (
            f"<!DOCTYPE html>\n"
            f"<html lang=\"en\">\n"
            f"<head>\n"
            f"    <meta charset=\"UTF-8\">\n"
            f"    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"    <title>{self.title}</title>\n"
            f"    <style>\n"
            f"        * {{\n"
            f"            margin: 0;\n"
            f"            padding: 0;\n"
            f"            box-sizing: border-box;\n"
            f"        }}\n"
            f"\n"
            f"        body {{\n"
            f"            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;\n"
            f"            line-height: 1.6;\n"
            f"            color: #333;\n"
            f"            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n"
            f"            min-height: 100vh;\n"
            f"            padding: 20px;\n"
            f"        }}\n"
            f"\n"
            f"        .container {{\n"
            f"            max-width: 1200px;\n"
            f"            margin: 0 auto;\n"
            f"        }}\n"
            f"\n"
            f"        header {{\n"
            f"            text-align: center;\n"
            f"            color: white;\n"
            f"            margin-bottom: 40px;\n"
            f"            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);\n"
            f"        }}\n"
            f"\n"
            f"        h1 {{\n"
            f"            font-size: 2.5em;\n"
            f"            margin-bottom: 10px;\n"
            f"        }}\n"
            f"\n"
            f"        .milestone-card {{\n"
            f"            background: white;\n"
            f"            border-radius: 8px;\n"
            f"            padding: 20px;\n"
            f"            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);\n"
            f"            transition: transform 0.2s, box-shadow 0.2s;\n"
            f"            margin: 10px;\n"
            f"        }}\n"
            f"\n"
            f"        .milestone-card:hover {{\n"
            f"            transform: translateY(-4px);\n"
            f"            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);\n"
            f"        }}\n"
            f"\n"
            f"        .milestone-card h3 {{\n"
            f"            color: #667eea;\n"
            f"            margin-bottom: 10px;\n"
            f"            font-size: 1.3em;\n"
            f"        }}\n"
            f"\n"
            f"        .milestone-link {{\n"
            f"            display: inline-block;\n"
            f"            padding: 8px 16px;\n"
            f"            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n"
            f"            color: white;\n"
            f"            text-decoration: none;\n"
            f"            border-radius: 4px;\n"
            f"            transition: opacity 0.2s;\n"
            f"            float: right;\n"
            f"        }}\n"
            f"\n"
            f"        .milestone-link:hover {{\n"
            f"            opacity: 0.9;\n"
            f"        }}\n"
            f"\n"
            f"        footer {{\n"
            f"            text-align: center;\n"
            f"            color: rgba(255, 255, 255, 0.8);\n"
            f"            margin-top: 40px;\n"
            f"            font-size: 0.9em;\n"
            f"        }}\n"
            f"    </style>\n"
            f"</head>\n"
            f"<body>\n"
            f"    <div class=\"container\">\n"
            f"        <header>\n"
            f"            <h1>{self.title}</h1>\n"
            f"            <p class=\"subtitle\">Open Milestones</p>\n"
            f"        </header>\n"
            f"\n"
            f"        <div class=\"milestones-grid\">\n"
            f"{milestone_html}\n"
            f"        </div>\n"
            f"\n"
            f"        <footer>\n"
            f"            <p>Generated by Jira Milestone Reporter on {generated_at}</p>\n"
            f"        </footer>\n"
            f"    </div>\n"
            f"</body>\n"
            f"</html>\n"
        )

        # Write file
        output_file = output_dir / "index.html"
        output_file.write_text(html_content, encoding="utf-8")
        logger.info(f"Index saved to: {output_file}")

        return output_file

    def render_milestone_report(
        self, milestone: Dict, issues: List[Dict], output_dir: Path
    ) -> Path:
        """Generate detailed milestone report with issue table.

        Args:
            milestone: Milestone dictionary with id, name, description
            issues: List of issue dictionaries for this milestone
            output_dir: Output directory path

        Returns:
            Path to generated milestone HTML file
        """
        logger.info(f"Rendering milestone report: {milestone.get('name')}")

        # Create output dir if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build issue table rows
        issue_rows = []
        for issue in issues:
            key = issue.get("key", "")
            summary = issue.get("summary", "")
            status = issue.get("status", "To Do")
            due_date = issue.get("due_date", "")
            start_date = issue.get("start_date", "")
            assignee = issue.get("assignee", "Unassigned")

            # Format dates
            due_date_str = due_date if due_date else "-"
            start_date_str = start_date if start_date else "-"

            # Status badge color
            if status == "Done":
                status_color = "green"
            elif status == "In Progress":
                status_color = "orange"
            else:
                status_color = "gray"

            issue_url = self._get_issue_url(key)

            row_html = (
                f"        <tr>\n"
                f'            <td><a href="{issue_url}" target="_blank">{key}</a></td>\n'
                f"            <td>{summary}</td>\n"
                f'            <td><span class="status status-{status_color}">'
                f"{status}</span></td>\n"
                f"            <td>{start_date_str}</td>\n"
                f"            <td>{due_date_str}</td>\n"
                f"            <td>{assignee}</td>\n"
                f"        </tr>"
            )
            issue_rows.append(row_html)

        issue_table = "\n".join(issue_rows)
        milestone_name = milestone.get("name", "Unknown")

        # Generate table or no-issues message
        if issues:
            table_html = (
                "        <table class=\"issues-table\">\n"
                "            <thead>\n"
                "                <tr>\n"
                "                    <th>Issue Key</th>\n"
                "                    <th>Summary</th>\n"
                "                    <th>Status</th>\n"
                "                    <th>Start Date</th>\n"
                "                    <th>Due Date</th>\n"
                "                    <th>Assignee</th>\n"
                "                </tr>\n"
                "            </thead>\n"
                "            <tbody>\n"
                f"{issue_table}\n"
                "            </tbody>\n"
                "        </table>"
            )
        else:
            table_html = (
                '<div class="no-issues">'
                "No issues found in this milestone."
                "</div>"
            )

        # Generate HTML
        html_content = (
            f"<!DOCTYPE html>\n"
            f"<html lang=\"en\">\n"
            f"<head>\n"
            f"    <meta charset=\"UTF-8\">\n"
            f"    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"    <title>{milestone_name} - {self.title}</title>\n"
            f"    <style>\n"
            f"        * {{\n"
            f"            margin: 0;\n"
            f"            padding: 0;\n"
            f"            box-sizing: border-box;\n"
            f"        }}\n"
            f"\n"
            f"        body {{\n"
            f"            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;\n"
            f"            line-height: 1.6;\n"
            f"            color: #333;\n"
            f"            background: #f5f5f5;\n"
            f"            padding: 20px;\n"
            f"        }}\n"
            f"\n"
            f"        .container {{\n"
            f"            max-width: 1400px;\n"
            f"            margin: 0 auto;\n"
            f"            background: white;\n"
            f"            border-radius: 8px;\n"
            f"            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);\n"
            f"            padding: 30px;\n"
            f"        }}\n"
            f"\n"
            f"        header {{\n"
            f"            margin-bottom: 30px;\n"
            f"            border-bottom: 2px solid #667eea;\n"
            f"            padding-bottom: 20px;\n"
            f"        }}\n"
            f"\n"
            f"        h1 {{\n"
            f"            color: #667eea;\n"
            f"            margin-bottom: 5px;\n"
            f"        }}\n"
            f"\n"
            f"        .breadcrumb {{\n"
            f"            color: #999;\n"
            f"            font-size: 0.9em;\n"
            f"            margin-top: 10px;\n"
            f"        }}\n"
            f"\n"
            f"        .breadcrumb a {{\n"
            f"            color: #667eea;\n"
            f"            text-decoration: none;\n"
            f"        }}\n"
            f"\n"
            f"        .issues-table {{\n"
            f"            width: 100%;\n"
            f"            border-collapse: collapse;\n"
            f"        }}\n"
            f"\n"
            f"        .issues-table th {{\n"
            f"            text-align: left;\n"
            f"            padding: 12px;\n"
            f"            font-weight: 600;\n"
            f"            color: #667eea;\n"
            f"            font-size: 0.9em;\n"
            f"        }}\n"
            f"\n"
            f"        .issues-table td {{\n"
            f"            padding: 12px;\n"
            f"            border-bottom: 1px solid #eee;\n"
            f"        }}\n"
            f"\n"
            f"        .issues-table a {{\n"
            f"            color: #667eea;\n"
            f"            text-decoration: none;\n"
            f"        }}\n"
            f"\n"
            f"        .status {{\n"
            f"            display: inline-block;\n"
            f"            padding: 4px 8px;\n"
            f"            border-radius: 4px;\n"
            f"            font-size: 0.85em;\n"
            f"            font-weight: 600;\n"
            f"        }}\n"
            f"\n"
            f"        .status-green {{\n"
            f"            background: #d4edda;\n"
            f"            color: #155724;\n"
            f"        }}\n"
            f"\n"
            f"        .status-orange {{\n"
            f"            background: #fff3cd;\n"
            f"            color: #856404;\n"
            f"        }}\n"
            f"\n"
            f"        .status-gray {{\n"
            f"            background: #e9ecef;\n"
            f"            color: #383d41;\n"
            f"        }}\n"
            f"\n"
            f"        footer {{\n"
            f"            margin-top: 40px;\n"
            f"            padding-top: 20px;\n"
            f"            border-top: 1px solid #eee;\n"
            f"            text-align: center;\n"
            f"            color: #999;\n"
            f"            font-size: 0.9em;\n"
            f"        }}\n"
            f"    </style>\n"
            f"</head>\n"
            f"<body>\n"
            f"    <div class=\"container\">\n"
            f"        <header>\n"
            f"            <h1>{milestone_name}</h1>\n"
            f"            <div class=\"breadcrumb\">\n"
            f"                <a href=\"index.html\">Back to Milestones</a>\n"
            f"            </div>\n"
            f"        </header>\n"
            f"\n"
            f"        <h2 style=\"margin-bottom: 20px; color: #333;\">"
            f"Issues ({len(issues)})</h2>\n"
            f"\n"
            f"{table_html}\n"
            f"\n"
            f"        <footer>\n"
            f"            <p>Generated by Jira Milestone Reporter on {generated_at}</p>\n"
            f"        </footer>\n"
            f"    </div>\n"
            f"</body>\n"
            f"</html>\n"
        )

        # Write file
        milestone_id = milestone.get("id", "unknown")
        output_file = output_dir / f"milestone-{milestone_id}.html"
        output_file.write_text(html_content, encoding="utf-8")
        logger.info(f"Milestone report saved to: {output_file}")

        return output_file
