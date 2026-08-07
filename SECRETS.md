# Secrets & tokens the engine uses

Add these under **repo → Settings → Secrets and variables → Actions**.
Two tabs there: **Secrets** (encrypted values) and **Variables** (plain config).

Until a source's key is set, that source emits **sample** data — the pipeline
still runs end to end. So you can add these incrementally.

## Required for real briefs

| Secret | What it's for | Where to get it |
|--------|---------------|-----------------|
| `ANTHROPIC_API_KEY` | Writes the briefs (Claude) | console.anthropic.com → **Settings → API Keys → Create Key** |
| `AIRTABLE_TOKEN` | Writes the trend board | airtable.com/create/tokens → **Create token**, scopes `data.records:read`, `data.records:write`, `schema.bases:read`, and grant it your base |
| `AIRTABLE_BASE_ID` | Which base to write to | Open the base → **Help → API documentation**; the ID starts with `app…` (also visible in the base URL) |
| `SLACK_TOKEN` | Posts the shortlist | api.slack.com/apps → **Create app** → **OAuth & Permissions** → add scope `chat:write` → **Install to workspace** → copy the **Bot User OAuth Token** (`xoxb-…`) |
| `SLACK_CHANNEL` | Channel to post in | In Slack, open the channel → **View channel details** → copy the **Channel ID** (`C…`) and invite the bot to it |

## Optional source keys (each unlocks one live source)

| Secret | Source | Where to get it |
|--------|--------|-----------------|
| `AHREFS_API_KEY` | Ahrefs search demand | ahrefs.com → **API** dashboard |
| `SERPAPI_KEY` | SERP features | serpapi.com → **Dashboard → API Key** |
| `YOUTUBE_API_KEY` | YouTube signals | console.cloud.google.com → enable **YouTube Data API v3** → **Create credentials → API key** |
| `NEWS_API_KEY` | News mentions | newsapi.org → register → **API key** |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Reddit discussion | reddit.com/prefs/apps → **Create app** (type: *script*) → copy the id (under the name) and the secret |
| `GSC_CREDENTIALS` | Google Search Console | Google Cloud → create a **service account**, enable **Search Console API**, download the **JSON key**, add the service-account email as a user in Search Console. Paste the whole JSON as the secret value |

## Automation / cross-repo (optional)

| Name | Type | What it's for |
|------|------|---------------|
| `REPO_PAT` | **Secret** | Lets `monthly-refresh.yml` trigger sibling repos. Create a fine-grained PAT with **Contents: Read & write** on the repos you want to poke (or classic PAT with `repo` scope) and store it here |
| `SIBLING_REPOS` | **Variable** | Comma-separated `owner/repo,owner/repo` list the monthly run fans out to. Leave unset to skip fan-out |

## Adding one

Settings → Secrets and variables → Actions → **New repository secret** → name it
exactly as above → paste the value → **Add secret**. Variables use the
**Variables** tab → **New repository variable**.
