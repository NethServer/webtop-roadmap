# Jira Milestone Reporter

Generate shareable, static HTML milestone reports for all open milestones in your Jira project.

## Overview
The Jira Milestone Reporter is a Python utility that:

- **Connects to your Jira Cloud instance** via REST API
- **Fetches all Epic issues as milestones** from your project (e.g., WT-1421 "Milestone 2")
- **For each milestone Epic, generates a detailed report** showing all child issues with:
  - Issue key, summary, current status
  - Start date and due date (if available)
  - Assignee information
- **Creates an index page** with links to all milestone reports
- **Outputs professional, self-contained HTML files** that can be shared and viewed in any browser

Perfect for project tracking, release planning, milestone dashboards, and automated progress reporting.


## Prerequisites

- **Python 3.8+** - The script is written in Python 3
- **Jira Cloud Account** - Must be an active Jira Cloud instance
- **API Token** - Generate at https://id.atlassian.com/manage-profile/security/api-tokens
- **Internet Connection** - To reach your Jira instance

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url> webtop-roadmap
cd webtop-roadmap
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Edit `.env` with your Jira credentials:

```bash
nano .env  # or use your preferred editor
```

#### 🔑 Configuration Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `JIRA_BASE_URL` | Yes | Your Jira Cloud instance URL | `https://mycompany.atlassian.net` |
| `JIRA_USERNAME` | Yes | Your Jira account email | `user@example.com` |
| `JIRA_API_TOKEN` | Yes | Your API token from https://id.atlassian.com/manage-profile/security/api-tokens | `ATATT3xFy...` |
| `JIRA_PROJECT_KEY` | Yes | Your Jira project key | `WT` or `PROJ` |
| `OUTPUT_DIR` | No | Output directory for HTML files (default: `./output`) | `./reports` |
| `TIMELINE_TITLE` | Yes | Title displayed on reports | `WebTop Release Reports` |
| `START_DATE_FIELD` | No | Custom start date field (optional, for special date tracking) | `customfield_10015` |

#### 📝 Configuration Example

Content of `.env` file:
```bash
# Your Jira instance
JIRA_BASE_URL=https://company.atlassian.net
# Your account
JIRA_USERNAME=user@example.com
# Your API token (get from https://id.atlassian.com/manage-profile/security/api-tokens)
JIRA_API_TOKEN=ATATT3xFy...
# Your project key (visible in Jira URLs like /browse/PROJ-123)
JIRA_PROJECT_KEY=WT
# Where to save the HTML reports
OUTPUT_DIR=./output
# Title for the reports
TIMELINE_TITLE="WebTop Milestone Reports"

# Optional: custom start date field
# START_DATE_FIELD=customfield_10015
```

## 📖 Usage

### Basic Usage

The script automatically loads the `.env` file from the project root directory:

```bash
python src/jira_milestone_reporter.py
```

The script will:
1. Load and validate configuration from environment variables.
2. Fetch all open Epic issues from your Jira project to serve as milestones.
3. For each Epic, fetch all its child issues.
4. Generate a detailed HTML report for each Epic that contains issues.
5. Create an `index.html` dashboard linking to all the generated reports.

## 📁 Output Files

The script generates:

```
output/
├── index.html                      # Dashboard with all milestones
├── milestone-5.24.0.html           # Detailed report for 5.24.0
├── milestone-5.25.0.html           # Detailed report for 5.25.0
└── milestone-5.25.3.html           # Detailed report for 5.25.3
```


## Automated Deployment with GitHub Actions

This project includes a GitHub Actions workflow to automatically generate and publish the reports to GitHub Pages.

### How It Works
- **Scheduled Run**: The workflow runs automatically every night.
- **Secure**: It uses repository secrets to securely access the Jira API.
- **Publish**: It commits the generated `output` directory to the `gh-pages` branch.

### Setup
1. **Add Secrets**: In your GitHub repository, go to `Settings > Secrets and variables > Actions` and add the following repository secrets:
   - `JIRA_BASE_URL`
   - `JIRA_USERNAME`
   - `JIRA_API_TOKEN`
   - `JIRA_PROJECT_KEY`
2. **Enable GitHub Pages**: Go to your repository's `Settings > Pages` and configure it to deploy from the `gh-pages` branch.

The reports will be available at `https://<your-username>.github.io/<your-repo-name>/`.

## Testing

To run the full test suite:
```bash
pytest tests/
```

## Troubleshooting

- **401 Unauthorized**: Check that your `JIRA_USERNAME` and `JIRA_API_TOKEN` are correct.
- **404 Not Found**: Ensure `JIRA_BASE_URL` and `JIRA_PROJECT_KEY` are correct and that you have access to the project.
- **No Milestones Found**: Verify that there are open Epic issues in your project that are not in a "Done" status category.
