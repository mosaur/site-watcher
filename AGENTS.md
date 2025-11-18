# Repository Guidelines

## Project Structure & Module Organization
The automation lives at `lsc.py`, which wraps Playwright’s synchronous API to crawl Loadstar Capital listings, diff against `estates.json`, and notify Slack. Persistent state (latest estate snapshot) is stored in `estates.json`; keep the JSON small and UTF-8 encoded so diffs remain readable. `config.example.json` documents the required secrets; create `config.json` for local runs (auto-ignored). `myenv/` is a local virtual environment (omit it from commits) and `README.md` only names the repo, so new docs belong here until a fuller README is written. Add new modules under the root, grouped by concern (e.g., `notifiers/`, `scrapers/`) and update import paths accordingly.

## Build, Test, and Development Commands
Python 3.11+ is expected. Typical setup:
```
python3 -m venv myenv && source myenv/bin/activate
pip install playwright schedule jpholiday slackweb
playwright install chromium
```
Run the watcher with `python lsc.py`; it launches Chromium headless and schedules the main loop every eight hours. For ad-hoc runs without the scheduler, temporarily swap `common_process_run` into `run()` and execute `python lsc.py`.

## Coding Style & Naming Conventions
Follow standard PEP 8: four-space indentation, snake_case for functions/variables, and descriptive module-level constants (e.g., `SLACK_WEBHOOK_URL`). Keep sleep intervals, selectors, and URLs near the top of the file so operators can adjust them quickly. Use explicit UTF-8 when reading/writing estate data, and keep random waits deterministic for tests by threading in a seed parameter.

## Testing Guidelines
There is no formal test suite yet. At minimum, add smoke tests around `get_all_estate` that mock Playwright pages (pytest + `pytest-playwright` works well) and ensure Japanese text persists correctly. When modifying Slack logic, run a dry pass by stubbing `slackweb.Slack` and verifying the diff payload. Manual verification remains critical: run `python lsc.py` once, confirm the console shows the expected estate count, and check Slack for the formatted notice.

## Commit & Pull Request Guidelines
Existing history uses short imperative subjects (“initial”), so keep messages ≤50 chars, imperative, and English or Japanese for consistency. Each pull request should describe the user-facing impact, list environment/setup changes (new secrets, cron intervals), and attach relevant console output or Slack screenshots when altering notifications. Reference issue numbers using `Fixes #123` so deployment automation knows what to close.

## Security & Configuration Tips
Do not commit real Slack webhooks; copy `config.example.json` to `config.json`, set `slack_webhook_url`, and keep the latter out of Git (already ignored). When testing locally, rotate hooks frequently and keep Playwright dependencies updated (`pip install -U playwright`). If this script is scheduled via launchd or cron, document the job file alongside the code so other operators can reproduce the schedule.

## Agent-Specific Instructions
All written responses for this project must follow the Japanese guidelines in `japanese.md`. Read that file before drafting PRs, issues, or review comments so every explanation, aside from required code snippets, is delivered in Japanese.
