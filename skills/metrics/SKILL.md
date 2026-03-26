---
name: metrics
description: "Query and analyze metrics from the dbt semantic layer using MetricFlow"
argument-hint: "[metric-name] [--list] [--dimensions dim1,dim2] [--grain day|week|month|quarter] [--range last_30_days|last_90_days|last_12_months]"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **mf** (MetricFlow CLI): Run `which mf`. If missing, install via `pipx inject --include-apps dbt-bigquery dbt-metricflow` (if dbt was installed via pipx) or `pip install dbt-metricflow[bigquery]`
3. **dbt**: Run `which dbt`. If missing, install via `pipx install dbt-bigquery`
4. **pipx**: Run `which pipx`. If missing, install via `brew install pipx`
5. **pm-os/metrics repo**: Check if `~/.pm-os/metrics` exists. If missing, clone it:
   ```
   mkdir -p ~/.pm-os && git clone git@ghe.spotify.net:pm-os/metrics.git ~/.pm-os/metrics
   ```
6. **dbt packages**: Run `cd ~/.pm-os/metrics && dbt deps --quiet && dbt parse` to ensure the semantic manifest is generated.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Metrics Query Skill

**CRITICAL: NEVER use the BigQuery MCP tool (mcp__bigquery-mcp__execute_query). ALWAYS use the MetricFlow CLI (`mf`) via Bash.**

Query metrics from the PM-OS dbt semantic layer using the MetricFlow CLI (`mf`). Metrics are defined in the pm-os/metrics repo and can be either simple (based on a single measure) or derived (combining multiple metrics).

## ⚠️ Important: Use MetricFlow CLI Only

- **DO:** Use `mf query` via Bash tool
- **DO NOT:** Use `mcp__bigquery-mcp__execute_query` or any BigQuery MCP tool
- **Reason:** MetricFlow handles semantic layer correctly and has proper auth

## Prerequisites Check

Before running any metric queries, perform these checks:

### 1. Check if MetricFlow is installed

```bash
which mf || echo "MetricFlow CLI not installed"
```

If MetricFlow is NOT installed, walk the user through installation:

```bash
# If dbt was installed via pipx (check with: pipx list | grep dbt)
pipx inject --include-apps dbt-bigquery dbt-metricflow

# If dbt was installed via pip
pip install dbt-metricflow[bigquery]

# Verify installation
mf --version
```

**Note:** If dbt is installed via pipx, you MUST use `pipx inject` to add dbt-metricflow to the same virtual environment.

### 2. Clone or update the metrics repo

The dbt project lives at: `https://ghe.spotify.net/pm-os/metrics`

Clone to a standard location if it doesn't exist:

```bash
# Check if repo exists, clone if not
if [ ! -d ~/.pm-os/metrics ]; then
    mkdir -p ~/.pm-os
    git clone git@ghe.spotify.net:pm-os/metrics.git ~/.pm-os/metrics
fi

# Update to latest
cd ~/.pm-os/metrics && git pull --quiet
```

### 3. Generate the semantic manifest (first time or after updates)

MetricFlow requires a parsed dbt project. If you see "Unable to load the semantic manifest" error, run:

```bash
cd ~/.pm-os/metrics && dbt deps --quiet && dbt parse
```

This generates `target/semantic_manifest.json` which MetricFlow needs.

**Important:** All `mf` commands must be run from the metrics repo directory:
```
~/.pm-os/metrics
```

## Available Commands

### 1. List Available Metrics (--list)

```bash
cd ~/.pm-os/metrics && mf list metrics
```

This shows all metrics with their available dimensions.

### 2. List Dimensions for a Metric

```bash
cd ~/.pm-os/metrics && mf list dimensions --metrics <metric_name>
```

### 3. Query a Metric

Basic syntax:
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics <metric_name> \
  --group-by <dimension> \
  [--start-time YYYY-MM-DD] \
  [--end-time YYYY-MM-DD] \
  [--limit N] \
  [--order <dimension>]
```

### 4. Show Generated SQL (--explain)

Add `--explain` to see the SQL that would be executed:
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics <metric_name> \
  --group-by metric_time__month \
  --explain
```

### 5. Export to CSV

```bash
cd ~/.pm-os/metrics && mf query \
  --metrics <metric_name> \
  --group-by metric_time__month \
  --csv /tmp/output.csv
```

## Time Grain Options

MetricFlow uses the pattern `metric_time__<grain>` for time grouping:

| Grain | Dimension |
|-------|-----------|
| Day | `metric_time__day` |
| Week | `metric_time__week` |
| Month | `metric_time__month` |
| Quarter | `metric_time__quarter` |
| Year | `metric_time__year` |

## Date Range Options

Use `--start-time` and `--end-time` with ISO8601 dates:

| Range | Start Time |
|-------|------------|
| Last 7 days | 7 days ago from today |
| Last 30 days | 30 days ago from today |
| Last 90 days | 90 days ago from today |
| Last 12 months | 12 months ago from today |

Calculate dates dynamically:
```bash
START_DATE=$(date -v-12m +%Y-%m-%d)  # 12 months ago (macOS)
# or
START_DATE=$(date -d "12 months ago" +%Y-%m-%d)  # Linux
```

## Example Queries

### List all metrics
```bash
cd ~/.pm-os/metrics && mf list metrics
```

### Query percentage of Accounting-owned uplifts (monthly, last 12 months)
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics pct_accounting_owned_uplifts \
  --group-by metric_time__month \
  --start-time $(date -v-12m +%Y-%m-%d) \
  --order metric_time__month
```

### Query NetSuite export counts by type
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics netsuite_export_count \
  --group-by metric_time__month,export__export_type \
  --start-time $(date -v-6m +%Y-%m-%d) \
  --order metric_time__month
```

### Query multiple metrics together
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics total_uplift_count,accounting_uplift_count,pct_accounting_owned_uplifts \
  --group-by metric_time__month \
  --start-time $(date -v-12m +%Y-%m-%d)
```

### Show SQL for a query (debugging)
```bash
cd ~/.pm-os/metrics && mf query \
  --metrics pct_accounting_owned_uplifts \
  --group-by metric_time__month \
  --explain
```

## Query Guardrails (from CLAUDE.md)

Before running any query:
1. State the **product question** being answered
2. State the **hypothesis** or expected pattern
3. Limit results to aggregated data (no raw user-level data)

## Presenting Results

After running a query, present results as:
- A summary of the metric (current value, trend if time series)
- A markdown table showing the data
- For time series: describe the trend (increasing, decreasing, stable)
- Calculate month-over-month or period-over-period changes when relevant

## Troubleshooting

### "mf not found"
MetricFlow CLI is not installed. Run:
```bash
pipx inject --include-apps dbt-bigquery dbt-metricflow
```

### "No metrics found" or "Unable to load the semantic manifest"
The dbt project needs to be parsed first:
```bash
cd ~/.pm-os/metrics && dbt deps --quiet && dbt parse
```
Then retry:
```bash
cd ~/.pm-os/metrics && mf list metrics
```

### Permission denied on BigQuery
Authenticate with gcloud:
```bash
gcloud auth application-default login
```

### Cannot clone repo
Make sure you're connected to VPN and have GHE access:
```bash
ssh -T git@ghe.spotify.net
```

### Metric not recognized
List available metrics to verify the name:
```bash
cd ~/.pm-os/metrics && mf list metrics
```

## Repo Location

- **Remote:** https://ghe.spotify.net/pm-os/metrics
- **Local clone:** ~/.pm-os/metrics

To view semantic model definitions, read the YAML files in the cloned repo:
```bash
ls ~/.pm-os/metrics/models/staging/*/_*_semantic.yml
```
