---
name: vedder
description: "Ask questions about Spotify data using Vedder's conversational AI — text-to-SQL across 115+ BigQuery clusters"
argument-hint: "<your question about Spotify data>"
allowed-tools: ["Bash", "Read"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **curl**: Run `which curl`. If missing, install via `brew install curl`
3. **gcloud auth**: Run `gcloud auth print-access-token`. If missing or expired, run `gcloud auth login`
4. **VPN connection**: Vedder requires VPN access to reach `backstage-proxy.spotify.net`. Ensure you are connected to the Spotify VPN.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Vedder — Conversational Data Queries

Ask questions about Spotify data in plain English. Vedder translates your question into SQL, runs it against BigQuery, and returns the answer. It has access to 115+ data clusters covering ads, streaming, commerce, podcasts, internal tools, and more.

## How It Works

Vedder's conversational API accepts a natural language question and returns a streaming response. Under the hood it:
1. Identifies which data cluster(s) are relevant
2. Generates SQL from your question
3. Executes against BigQuery
4. Returns a human-readable answer

## Prerequisites

You need `gcloud` authenticated:
```bash
gcloud auth print-access-token > /dev/null 2>&1 || gcloud auth login
```

## Querying Vedder

Use the conversational streaming endpoint. Parse the SSE response and extract the final answer.

### Single question (no conversation context)

```bash
curl -s --max-time 120 -N \
  -X POST "https://backstage-proxy.spotify.net/api/insights-service-conversational/v1/chat/stream" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"message": "<USER_QUESTION>"}' 2>&1
```

### Follow-up question (within a conversation)

To ask a follow-up, include the `conversation_id` from the previous response:

```bash
curl -s --max-time 120 -N \
  -X POST "https://backstage-proxy.spotify.net/api/insights-service-conversational/v1/chat/stream" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"message": "<FOLLOW_UP_QUESTION>", "conversation_id": "<CONVERSATION_ID>"}' 2>&1
```

## Parsing the Response

The API returns Server-Sent Events (SSE). Each line starts with `data: ` followed by JSON. The key event types:

| Event type | What it contains |
|---|---|
| `session_id` | Contains `conversation_id` — save this for follow-ups |
| `thinking` | Status messages about what Vedder is doing (e.g., "Generating SQL") |
| `text` | Partial text content as it streams |
| `final_response` | The complete answer — **use this as the result** |
| `sql` | The generated SQL query (if applicable) |
| `complete` | Stream is finished |
| `done` | End of response |

### Extracting the answer

To extract the final response from the SSE stream:

```bash
curl -s --max-time 120 -N \
  -X POST "https://backstage-proxy.spotify.net/api/insights-service-conversational/v1/chat/stream" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"message": "<USER_QUESTION>"}' 2>&1 \
  | grep '^data: ' \
  | sed 's/^data: //' \
  | python3 -c "
import sys, json
conv_id = None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        evt = json.loads(line)
        if evt.get('type') == 'session_id':
            conv_id = evt.get('conversation_id')
        if evt.get('type') == 'final_response':
            print(evt['content'])
            if conv_id:
                print(f'\n---\nconversation_id: {conv_id}')
    except json.JSONDecodeError:
        pass
"
```

## Presenting Results

1. Run the curl command with the user's question
2. Parse the SSE stream to extract the `final_response`
3. Present the answer to the user in markdown — it typically includes tables and summaries
4. If the response includes SQL (`sql` event), you can mention it but don't show it unless asked
5. Save the `conversation_id` — if the user asks a follow-up, include it in the next request

## Listing Available Clusters

To see what data is available:

```bash
curl -s --max-time 30 \
  "https://backstage-proxy.spotify.net/api/insights-service-conversational/v1/clusters/summaries" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" 2>&1 \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data:
    print(f\"{c.get('name', 'unknown'):40s} {c.get('description', '')[:80]}\")
"
```

## Example Queries

These are real questions you can ask:

- "How many ad impressions did we serve last month?"
- "What's the breakdown of streams by platform?"
- "Show me commerce dispute trends over the last 6 months"
- "How many active podcasters do we have?"
- "What are the top support channels by volume?"
- "Show me GCP billing trends by project"

## Troubleshooting

### "401 Unauthorized"
Re-authenticate with gcloud:
```bash
gcloud auth login
```

### Timeout or no response
The query may be complex. Increase `--max-time` or simplify the question.

### "No clusters found" for a topic
Ask Vedder what clusters are available: "What data clusters do you have?"
The response will list all 115+ available clusters.

## API Reference

- **Base URL:** `https://backstage-proxy.spotify.net/api/insights-service-conversational`
- **Repo:** [analytics-platform-tooling/insights-service](https://ghe.spotify.net/analytics-platform-tooling/insights-service)
- **Backstage:** [Vedder on Backstage](https://backstage.spotify.net/plugins/vedder)
