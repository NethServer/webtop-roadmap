That is an updated, action-oriented agent specification derived from `agents.md`, rewritten to implement the new scope: generate an index of open milestones and a per-milestone HTML file listing issues, states, dates, and assignees.

# 🧑‍💻 Agent: Jira Milestone Reporter

This agent enumerates open milestones (Fix Versions) for a Jira project and produces:
- A single index HTML file listing all open milestones as clickable links.
- One HTML file per milestone listing all issues in that milestone with status, dates (if present), assignee, and direct links to the Jira issue.

| Key | Value |
| :--- | :--- |
| **Name** | `Jira Milestone Reporter` |
| **Agent Type** | Data Extractor & Static HTML Renderer |
| **Goal** | Produce an index of open milestones and per-milestone HTML reports showing issues with current state, dates (if present), and assignees. |
| **Trigger** | Scheduled (Cron) or manual run. |
| **Input** | Environment variables (Jira credentials, project key, output directory). |
| **Output** | `index.html` and one HTML file per milestone (e.g., `milestone-<id|name>.html`). |
| **Dependencies** | Python 3.x, `requests` library. |

## Environment & Setup

All secrets and dynamic inputs must be sourced from the OS environment.

Mandatory configuration variables:
- JIRA_BASE_URL — root URL of Jira Cloud (e.g., https://yourdomain.atlassian.net)
- JIRA_USERNAME — email for Basic Auth
- JIRA_API_TOKEN — API token for Basic Auth
- JIRA_PROJECT_KEY — project key (e.g., PROJ)
- OUTPUT_DIR — directory where `index.html` and milestone files will be written (e.g., ./output)
- OPTIONAL: START_DATE_FIELD — custom field id for start date (e.g., customfield_10015). If unset, start date is read only if present in standard fields.
- OPTIONAL: TIMELINE_TITLE — title used in generated HTML pages

Authentication:
- Build Authorization header: "Basic " + Base64Encode(JIRA_USERNAME + ":" + JIRA_API_TOKEN)

## Execution Plan (Phases)

Phase 1 — Read env and prepare:
1. Read and validate required environment variables.
2. Create HTTP session with Authorization header and Accept: application/json.

Phase 2 — List open milestones:
1. Endpoint: GET {JIRA_BASE_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}/versions
2. Filter versions to "open" milestones: where `released` is false and `archived` is false (or other project conventions). Optionally include versions that are not marked released.
3. Build an in-memory list of milestones with id, name, releaseDate (if present), and description.

Phase 3 — Per-milestone issues extraction:
1. For each milestone, construct JQL:
      project = "{JIRA_PROJECT_KEY}" AND fixVersion = "{MILESTONE_NAME}"
2. Call search endpoint: POST or GET {JIRA_BASE_URL}/rest/api/3/search with payload/params:
      - jql
      - maxResults (handle pagination if > max)
      - fields: key, summary, status, duedate, assignee, (optionally) START_DATE_FIELD
3. If HTTP status >= 400, log/raise error and continue or abort per configured policy.

Phase 4 — Render HTML files:
1. Create OUTPUT_DIR if missing.
2. Generate index.html:
      - Title: TIMELINE_TITLE or "Milestone Index — {JIRA_PROJECT_KEY}"
      - List all open milestones as clickable links to corresponding milestone pages (use file names generated below).
      - For each milestone include brief metadata (release date if present, number of issues).
3. For each milestone generate milestone-<safe-id-or-name>.html:
      - Title with milestone name
      - Summary header (releaseDate, description)
      - Table or list of issues with columns: Issue Key (link to {JIRA_BASE_URL}/browse/{KEY}), Summary, Status (name), Start Date (if present), Due Date (if present), Assignee (display name or email)
      - Optionally group issues by status (To Do / In Progress / Done) or display a simple table.
4. Write files with safe filenames (slugify milestone name or use id) to OUTPUT_DIR.

Phase 5 — Output & exit:
1. Return success and location of generated files (index + per-milestone files).
2. Exit non-zero on fatal errors (auth failure, missing env vars, API rate limits).

## Data handling details

- Issue fields:
  - status: use fields['status']['name']
  - assignee: if fields['assignee'] present use displayName or accountId; show "Unassigned" otherwise
  - dates: check `fields['duedate']` and optional START_DATE_FIELD; treat absent values as blank
- Link construction:
  - Issue link: {JIRA_BASE_URL}/browse/{issue.key}
  - Milestone file link: relative link to `milestone-<slug>.html`

## Error handling & pagination

- Handle pagination by iterating `startAt` until `total` reached.
- On HTTP error >= 400 log the error body and abort or continue based on a --fail-on-error flag.
- Sanitize milestone names to create filesystem-safe filenames.

## Testing & Validation

- Run locally with environment variables set and validate:
  - index.html lists expected open milestones with working links
  - Each milestone HTML contains expected issues with status, dates, and assignee
  - Issue links open Jira issue pages
- Example test command:
  source .env && python src/jira_milestone_reporter.py

## Files & Storage conventions

- OUTPUT_DIR/index.html — list of open milestones
- OUTPUT_DIR/milestone-<slug>.html — per milestone report
- Save any intermediate plan or generated agent plan files under plans/ per `AGENTS.md` guidelines:
  - plans/intermediate/
  - plans/final/

## Notes & Extensions (optional)

- Add CSS for nicer tables and mobile-friendly layouts.
- Add caching or ETag handling to reduce API calls.
- Optionally include a small client-side filter (JavaScript) to search/filter milestones or issues.

This specification is self-contained and actionable for an implementation that uses the Jira REST API, reads secrets from environment variables, and writes static HTML reports into the specified output directory.
