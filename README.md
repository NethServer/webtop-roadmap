# 🎯 Jira Milestone Reporter

Generate shareable, static HTML milestone reports for all open milestones in your Jira project.

## 📋 Overview

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

## ✨ Features

- ✅ **Epic-Based Milestone Discovery** - Automatically discovers all Epic issues as milestones; no hardcoding needed
- ✅ **Child Issue Linking** - Automatically finds all issues linked to each Epic milestone
- ✅ **Secure** - No credentials stored in code; supports API token authentication
- ✅ **Clean HTML Tables** - Issue details in professional, easy-to-read tables
- ✅ **Status Badges** - Color-coded status indicators (Done, In Progress, To Do)
- ✅ **Date Tracking** - Display start and due dates when available
- ✅ **Assignee Info** - See who's responsible for each issue
- ✅ **Navigation Links** - Clickable links between index and detail pages
- ✅ **Direct Jira Links** - Click issue keys to jump to Jira
- ✅ **Beautiful Output** - Responsive design, gradient backgrounds, professional styling
- ✅ **Schedulable** - Can be run as a cron job for daily updates
- ✅ **Comprehensive Logging** - Detailed progress and error messages

## 📋 Prerequisites

- **Python 3.8+** - The script is written in Python 3
- **Jira Cloud Account** - Must be an active Jira Cloud instance
- **API Token** - Generate at https://id.atlassian.com/manage-profile/security/api-tokens
- **Internet Connection** - To reach your Jira instance

## 🚀 Installation

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

```bash
# Your Jira instance
export JIRA_BASE_URL=https://company.atlassian.net

# Your account
export JIRA_USERNAME=user@example.com

# Your API token (get from https://id.atlassian.com/manage-profile/security/api-tokens)
export JIRA_API_TOKEN=ATATT3xFy...

# Your project key (visible in Jira URLs like /browse/PROJ-123)
export JIRA_PROJECT_KEY=WT

# Where to save the HTML reports
export OUTPUT_DIR=./output

# Title for the reports
export TIMELINE_TITLE="WebTop Milestone Reports"

# Optional: custom start date field
# export START_DATE_FIELD=customfield_10015
```

## 📖 Usage

### Basic Usage

The script **automatically loads the `.env` file** from the project root directory:

```bash
python src/jira_milestone_reporter.py
```

**Note:** You no longer need to run `source .env` - the script loads it automatically!

The script will:
1. Load and validate configuration
2. Fetch all issues in the project and extract unique milestones from custom fields (customfield_10037 and customfield_10041)
3. For each milestone:
   - Search for all issues with that milestone
   - Generate a milestone-specific HTML report
4. Generate an index.html with links to all milestone reports
5. Save all files to the output directory

### Example Output

```
======================================================================
Jira Milestone Reporter
======================================================================
Phase 1: Loading configuration...
✓ Configuration and client initialized
Phase 2: Fetching project milestones...
Retrieved 10 Epic milestones from project
Phase 3: Filtering milestones...
Found 10 milestones (Epic issues)
Phase 4: Generating milestone reports...
  Processing milestone: Milestone 1 (WT-1237)
    Retrieved 50 issues
    ✓ Generated report for Milestone 1
  Processing milestone: Milestone 2 (WT-1421)
    Retrieved 20 issues
    ✓ Generated report for Milestone 2
  Processing milestone: Step 1 - 2023 (WT-1216)
    Retrieved 17 issues
    ✓ Generated report for Step 1 - 2023
Phase 5: Generating index.html...
✓ Generated index.html
======================================================================
✓ Success! Reports generated in: /home/user/webtop-roadmap/output
======================================================================
```

## 📁 Output Files

The script generates:

```
output/
├── index.html                      # Dashboard with all milestones
├── milestone-5.24.0.html           # Detailed report for 5.24.0
├── milestone-5.25.0.html           # Detailed report for 5.25.0
└── milestone-5.25.3.html           # Detailed report for 5.25.3
```

### Index Page (index.html)

- Lists all open milestones in a grid layout
- Shows milestone name, description, and issue count
- Clickable cards that link to each milestone's detailed report
- Professional gradient background and responsive design

### Milestone Report Pages (milestone-*.html)

- Detailed table of all issues in the milestone
- Columns: Issue Key, Summary, Status, Start Date, Due Date, Assignee
- Color-coded status badges:
  - 🟢 **Green** = Done
  - 🟠 **Orange** = In Progress
  - ⚪ **Gray** = To Do
- Issue keys are clickable links to Jira
- Back link to return to index.html

## 📅 Scheduling with Cron

Generate milestone reports automatically:

### Daily at 8 AM

```bash
0 8 * * * cd /home/user/webtop-roadmap && python src/jira_milestone_reporter.py
```

### Every Monday at 9 AM

```bash
0 9 * * 1 cd /home/user/webtop-roadmap && python src/jira_milestone_reporter.py
```

### Every 6 Hours

```bash
0 */6 * * * cd /home/user/webtop-roadmap && python src/jira_milestone_reporter.py
```

Edit your crontab:

```bash
crontab -e
```

## 🧪 Testing

### Running All Tests

```bash
pytest tests/
```

### Running Specific Test Suite

```bash
# Config tests
pytest tests/test_config.py -v

# Jira client tests
pytest tests/test_jira_client.py -v

# HTML renderer tests
pytest tests/test_html_renderer.py -v
```

### Running Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report
```

## 🔍 Troubleshooting

### Issue: "Missing required environment variables"

**Solution:** Ensure all mandatory variables are set:
```bash
# Check variables
env | grep -E "JIRA_|TIMELINE_|OUTPUT_"

# Or verify directly
echo "Base URL: $JIRA_BASE_URL"
echo "Project: $JIRA_PROJECT_KEY"
```

### Issue: "Jira API error (401): Unauthorized"

**Solution:** 
- Verify your `JIRA_USERNAME` (should be your email)
- Check that `JIRA_API_TOKEN` is correct
- Generate a new token at https://id.atlassian.com/manage-profile/security/api-tokens

### Issue: "Jira API error (404): Not found"

**Solution:**
- Verify `JIRA_BASE_URL` - should be like `https://company.atlassian.net` (no trailing slash)
- Check that the project key exists in Jira
- Verify you have access to the project

### Issue: "No open milestones found"

**Solution:**
- Check that the project has milestones/fix versions defined
- Verify that at least one milestone is not marked as released
- Verify that at least one milestone is not marked as archived

### Issue: "Failed to write output file"

**Solution:**
- Check that the output directory exists or can be created
- Verify write permissions on the output directory
- Ensure `OUTPUT_DIR` is a valid directory path

## 🔒 Security Best Practices

1. **Protect Your `.env` File**
   ```bash
   chmod 600 .env  # Only you can read
   ```

2. **Never Commit `.env`**
   ```bash
   echo ".env" >> .gitignore
   git rm --cached .env  # If already committed
   ```

3. **Use Project-Specific API Tokens**
   - Create separate tokens for different integrations
   - Limit token permissions if possible

4. **Rotate Tokens Periodically**
   - Delete old tokens at https://id.atlassian.com/manage-profile/security/api-tokens
   - Update credentials in your environment

5. **Monitor Access**
   - Check Jira login history for unauthorized access
   - Review API access logs

## 📦 Project Structure

```
webtop-roadmap/
├── src/                              # Source code
│   ├── jira_milestone_reporter.py    # Main script
│   ├── config.py                     # Environment configuration
│   ├── jira_client.py                # Jira API client
│   └── html_renderer.py              # HTML report renderer
├── tests/                            # Unit tests
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_jira_client.py
│   └── test_html_renderer.py
├── output/                           # Generated reports (default)
│   └── index.html
├── .env.example                      # Example configuration
├── .env                              # Your configuration (DO NOT COMMIT)
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── plans/                            # Implementation plans
```

## 🛠️ Development

### Understanding the Code Flow

1. **config.py** - Loads environment variables and validates configuration
2. **jira_client.py** - Handles API authentication and requests to Jira
   - `get_project_versions()` - Fetches all Epic issues as milestones
   - `search_issues()` - Fetches issues linked to an Epic milestone via "Epic Link" field
3. **html_renderer.py** - Generates HTML reports
   - `render_index()` - Creates dashboard with milestone cards
   - `render_milestone_report()` - Creates detailed issue table for each milestone Epic
4. **jira_milestone_reporter.py** - Main orchestrator
   - Phase 1: Initialize configuration and client
   - Phase 2: Fetch all Epic issues as project milestones
   - Phase 3: Filter to relevant milestones
   - Phase 4: Generate reports for each Epic milestone with its child issues
   - Phase 5: Generate index page

### Adding Custom Fields

The script currently fetches: `key`, `summary`, `status`, `duedate`, custom start date field

For Epic issues, it uses the Epic Link field to find child issues:
- Epic Link field: `customfield_10014` (used to query child issues)
- Epic Name field: `customfield_10011` (optional, for additional Epic metadata)

To add more fields:
1. Edit `src/jira_client.py` - Add to field list in `get_project_versions()` or `search_issues()`
2. Update `_normalize_issue()` to extract the new field
3. Update `html_renderer.py` to display it

### Customizing HTML Output

Edit `src/html_renderer.py`:
- Modify CSS styling (colors, fonts, layout)
- Change HTML structure and layout
- Add or remove columns in issue tables

## 📄 License

This project is part of the Webtop initiative.

## 🤝 Contributing

To contribute:

1. Test thoroughly with `pytest`
2. Follow PEP 8 style guidelines
3. Add tests for new features
4. Document changes
5. Update README if needed

## 📞 Support

For issues:

1. Check the **Troubleshooting** section
2. Review test files for usage examples
3. Examine logs for error details
4. Check Jira API docs: https://developer.atlassian.com/cloud/jira/rest/

## 🚀 Performance

- **Typical Execution Time**: 3-15 seconds (depends on number of milestones and issues)
- **API Rate Limits**: Jira Cloud allows 100 requests per second
- **Maximum Issues**: Script handles up to 500 issues per milestone
- **Maximum Milestones**: Script handles up to 100 milestones per project

## 🎓 Learning Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/rest/)
- [Fix Versions (Milestones) in Jira](https://support.atlassian.com/jira-software-cloud/docs/manage-versions-and-milestones/)
- [Python Requests Library](https://docs.python-requests.org/)
- [Jira Issue Status Categories](https://developer.atlassian.com/cloud/jira/software/rest/api-group-issues/#api-rest-api-3-status-get)

---

**Version**: 1.0  
**Last Updated**: 2025-01-10  
**Status**: Production Ready ✅
