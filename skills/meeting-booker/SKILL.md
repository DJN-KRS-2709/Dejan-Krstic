---
name: book
description: "Find available slot and book a meeting"
argument-hint: "\"Meeting Title\" with Anna, bob@spotify.com [30min|60min] [this week|next week]"
allowed-tools: ["Bash(*)", "Read(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **bq** (BigQuery CLI): Run `which bq`. It is included with the Google Cloud SDK. If missing, reinstall gcloud.
3. **curl**: Run `which curl`. If missing, install via `brew install curl`
4. **gcloud auth (calendar/cloud-platform scopes)**: Run `gcloud auth application-default print-access-token`. If missing or expired, run:
   ```
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform
   ```

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Meeting Booker Skill

Find the next available slot based on everyone's availability and book a meeting.

## Overview

This skill helps schedule meetings by:
1. Using gcloud Application Default Credentials (ADC) for authentication
2. Detecting the user's local timezone
3. Querying the Google Calendar freebusy API for all attendees
4. Finding mutually available time slots
5. Creating the event with attendees and Google Meet link

## Configuration

- **Default Duration:** 30 minutes
- **Working Hours:** 9:00 - 18:00 (user's local timezone)
- **Default Search Window:** Next 5 business days
- **GCP Project:** `fine-pm-em-staff` (for API quota)
- **Auth:** gcloud Application Default Credentials (no local token storage)
- **Timezone:** Automatically detected from user's system

---

## One-Time Setup

If calendar access hasn't been configured, the user needs to run:

```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform"
```

This opens a browser for Google sign-in. Credentials are managed by gcloud, not stored by this skill.

---

## Instructions

### Step 1: Check Authentication

Test if credentials have calendar scope:

```bash
TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null) && \
curl -s "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=$TOKEN" | grep -q calendar && echo "OK" || echo "NEEDS_SETUP"
```

#### If NEEDS_SETUP:

Tell the user:

```
Calendar access not configured. Run this command in your terminal:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform"

This will open a browser for Google sign-in. Then try /book again.
```

---

### Step 2: Detect User Timezone

Get the user's local timezone from the system:

```bash
# macOS
TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
echo "Timezone: $TZ"
```

This returns the IANA timezone (e.g., `Europe/Stockholm`, `America/New_York`, `Asia/Tokyo`).

**IMPORTANT:** Use this timezone for ALL operations:
- Displaying times to the user
- Setting event start/end times in the `timeZone` field
- Calculating working hours (9:00-18:00 in user's local time)
- Converting freebusy results for display

---

### Step 3: Parse Meeting Request

Parse the user's request to extract:
- **Title**: Meeting title (required - infer from context if not explicit)
- **Attendees**: List of people (required — emails, handles, or first names)
- **Duration**: Meeting length (default: 30 minutes)
- **Time Window**: When to search (default: next 5 business days)

Examples:
- `/book "Design Review" with Anna, bob@spotify.com`
- `/book "1:1 with Maria" with Maria 30min this week`
- `/book subledgers with Nate early next week` → Title: "Subledgers Discussion"
- `/book "sync" with Anna Hedin 30min` → full name, resolves directly

#### Step 3a: Classify each attendee input

For each attendee in the request, classify the input:

| Pattern | Type | Action |
|---------|------|--------|
| Contains `@` (e.g. `anna@spotify.com`) | Full email | Use as-is |
| Single word, all lowercase, no spaces (e.g. `ahedin`) | Handle | Append `@spotify.com` |
| Capitalized word or two words (e.g. `Anna`, `Anna Hedin`) | Name | Trigger name resolution (Step 3b) |

If all attendees resolve to emails without needing name lookup, skip directly to Step 4.

#### Step 3b: Resolve names via BigQuery

For each attendee classified as a name, query the BigQuery people dataset.

**Determine the latest available partition** (today, yesterday, or 2 days ago):

```bash
DATE_SUFFIX=$(date +%Y%m%d)
bq show "spotify-people:spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}" >/dev/null 2>&1 || \
  DATE_SUFFIX=$(date -v-1d +%Y%m%d) && \
  bq show "spotify-people:spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}" >/dev/null 2>&1 || \
  DATE_SUFFIX=$(date -v-2d +%Y%m%d)
echo "Using partition: $DATE_SUFFIX"
```

**For a first name only** (e.g. "Anna"):

```bash
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)

bq query --use_legacy_sql=false --format=json --max_rows=20 "
SELECT
  c.name,
  c.email,
  c.username,
  c.workday.work_role AS job_title,
  c.flattened_organization.squad AS squad,
  c.flattened_organization.product_area AS product_area,
  c.flattened_organization.studio AS studio,
  c.flattened_organization.mission AS mission,
  c.flattened_organization.alliance AS alliance,
  u.flattened_organization.squad AS user_squad,
  u.flattened_organization.product_area AS user_product_area,
  u.flattened_organization.studio AS user_studio,
  u.flattened_organization.mission AS user_mission,
  u.flattened_organization.alliance AS user_alliance
FROM \`spotify-people.spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}\` c
CROSS JOIN (
  SELECT flattened_organization
  FROM \`spotify-people.spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}\`
  WHERE LOWER(email) = LOWER('${USER_EMAIL}')
  LIMIT 1
) u
WHERE LOWER(c.name) LIKE LOWER('SEARCH_NAME %')
ORDER BY c.name
LIMIT 20
"
```

Replace `SEARCH_NAME` with the first name from the user's request.

**For a first + last name** (e.g. "Anna Hedin"):

Add an additional filter to narrow results:

```sql
WHERE LOWER(c.name) = LOWER('FIRST LAST')
```

This should typically return a single result.

#### Step 3c: Compute org distance

Compare the candidate's org fields to the current user's org fields to determine closeness. Check each level from most specific to least specific:

| Match level | Distance | Label |
|------------|----------|-------|
| Same squad | 0 | same squad |
| Same product area, different squad | 2 | same product area |
| Same studio, different product area | 4 | same studio |
| Same mission, different studio | 6 | same mission |
| Same alliance, different mission | 8 | same alliance |
| No common ancestor found | 10 | different org |

To compute: compare the `squad`, `product_area`, `studio`, `mission`, and `alliance` fields from the query results. The first matching level determines the distance. Rank candidates by distance (lowest first), then alphabetically by name.

#### Step 3d: Present results based on match count

**0 matches:**
```
No one named "Xyz" found in the directory.
Please provide their email address instead.
```

**1 match** — auto-resolve, confirm to user:
```
Resolved "Nate" → Nate Mehari (natemehari@spotify.com)
  Software Engineer · Accounting Automation — same product area
```

**2–10 matches** — rank by org distance, present options using `AskUserQuestion`:
```
Multiple people named "Anna". Closest to you:

1. Anna Hedin (ahedin@spotify.com)
   Senior Engineer · Payments Squad — same studio
2. Anna Gorka (agorka@spotify.com)
   Product Designer · Creator Tools — same alliance
3. Anna Smith (asmith@spotify.com)
   Data Scientist · Ad Platform — different org

Which Anna?
```

Use the `AskUserQuestion` tool with each person as an option. Include name, email, job title, squad, and org distance label.

**10+ matches:**
```
Too many people named "Anna" (N results). Try providing a last name:
  /book "sync" with Anna Hedin 30min
```

#### Step 3e: Multiple attendees to resolve

If the request includes multiple attendees that need name resolution (e.g. "with Anna and Nate"), resolve each name independently with separate BigQuery queries. You can run these queries in parallel.

Once all attendees are resolved to email addresses, proceed to Step 4.

---

### Step 4: Query Freebusy API

Query availability for ALL attendees (including the current user).

First, get the current user's email:
```bash
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
```

Then query freebusy:

```bash
TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
TOKEN=$(gcloud auth application-default print-access-token) && \
curl -s -X POST "https://www.googleapis.com/calendar/v3/freeBusy" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{
    "timeMin": "2026-02-09T09:00:00",
    "timeMax": "2026-02-12T18:00:00",
    "timeZone": "'"$TZ"'",
    "items": [
      {"id": "'"$USER_EMAIL"'"},
      {"id": "attendee@spotify.com"}
    ]
  }'
```

**Important:** Always include the `x-goog-user-project: fine-pm-em-staff` header for API quota.

**Time window calculation:**
- Convert user's request ("early this week", "next week", etc.) to ISO timestamps
- Use the detected timezone from Step 2
- Working hours: 9:00-18:00 in user's local timezone

---

### Step 5: Find Available Slots

Parse the freebusy response and find time slots where ALL attendees are free:

1. Merge all busy periods from all calendars
2. Find gaps during working hours (9:00-18:00 in user's timezone)
3. Filter for slots that fit the requested duration
4. Present 3-5 options to the user **in their local timezone**

Present options like this:

```
I checked both your calendars. Here are slots where you're both free:

1. Monday, Feb 9 at 11:00 AM (30 min)
2. Tuesday, Feb 10 at 11:30 AM (30 min)
3. Tuesday, Feb 10 at 4:00 PM (30 min)

Which slot works best?
```

---

### Step 6: Create Event with Attendees

Once the user confirms a slot, create the event using **the user's timezone**.

**IMPORTANT:** Always include the current user (`$USER_EMAIL`) in the attendees list so they appear on the invite, not just as the organizer.

```bash
TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
TOKEN=$(gcloud auth application-default print-access-token) && \
curl -s -X POST "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1&sendUpdates=all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{
    "summary": "Meeting Title",
    "description": "Meeting description",
    "start": {
      "dateTime": "2026-02-09T11:00:00",
      "timeZone": "'"$TZ"'"
    },
    "end": {
      "dateTime": "2026-02-09T11:30:00",
      "timeZone": "'"$TZ"'"
    },
    "attendees": [
      {"email": "'"$USER_EMAIL"'"},
      {"email": "attendee1@spotify.com"},
      {"email": "attendee2@spotify.com"}
    ],
    "conferenceData": {
      "createRequest": {
        "requestId": "meeting-'$(date +%s)'",
        "conferenceSolutionKey": {"type": "hangoutsMeet"}
      }
    },
    "reminders": {
      "useDefault": false,
      "overrides": [
        {"method": "popup", "minutes": 10}
      ]
    }
  }'
```

**Key parameters:**
- `sendUpdates=all` — Sends email invites to all attendees
- `conferenceDataVersion=1` — Required for Google Meet link
- `conferenceData.createRequest` — Generates a Meet link automatically
- `x-goog-user-project` — Required for API quota
- `timeZone` — **Must use user's detected timezone**

---

### Step 7: Confirm Booking

Parse the API response:

```json
{
  "id": "abc123",
  "htmlLink": "https://calendar.google.com/calendar/event?eid=...",
  "hangoutLink": "https://meet.google.com/xxx-yyyy-zzz",
  "attendees": [
    {"email": "attendee@spotify.com", "responseStatus": "needsAction"}
  ]
}
```

Report success (showing times in user's timezone):

```
Meeting booked!

**Meeting Title**
- When: Monday, February 9 at 11:00 AM - 11:30 AM
- Attendees: attendee@spotify.com (invite sent)
- Google Meet: https://meet.google.com/xxx-yyyy-zzz
- Calendar: [View event](https://calendar.google.com/calendar/event?eid=...)

All attendees will receive email invitations automatically.
```

---

## Time Window Calculations

| User says | Means |
|-----------|-------|
| "early this week" | Monday to Wednesday |
| "late this week" | Thursday to Friday |
| "this week" | Now until Friday |
| "next week" | Monday to Friday of next week |
| "early next week" | Monday to Wednesday of next week |
| "tomorrow" | Tomorrow 9 AM to 6 PM |
| "next few days" | Next 3 business days |

Always use the user's detected timezone for these calculations.

---

## Complete Example Flow

**User:** `/book subledger updates with natemehari@spotify.com 30min early this week`

**Step 1 - Check auth:**
```bash
TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null) && \
curl -s "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=$TOKEN" | grep -q calendar && echo "OK"
```
→ OK

**Step 2 - Detect timezone:**
```bash
TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
echo $TZ
```
→ Europe/Stockholm

**Step 3 - Parse request:**
- Title: "Subledger Updates"
- Attendees: natemehari@spotify.com
- Duration: 30 minutes
- Window: Mon Feb 9 - Wed Feb 11 (user's local time)

**Step 4 - Query freebusy:**
```bash
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
TOKEN=$(gcloud auth application-default print-access-token) && \
curl -s -X POST "https://www.googleapis.com/calendar/v3/freeBusy" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{
    "timeMin": "2026-02-09T09:00:00",
    "timeMax": "2026-02-12T18:00:00",
    "timeZone": "'"$TZ"'",
    "items": [
      {"id": "'"$USER_EMAIL"'"},
      {"id": "natemehari@spotify.com"}
    ]
  }'
```

**Step 5 - Find mutual availability and present:**
```
I checked both your calendars. Here are slots where you're both free:

1. Monday, Feb 9 at 11:00 AM (30 min)
2. Tuesday, Feb 10 at 11:30 AM (30 min)
3. Tuesday, Feb 10 at 4:00 PM (30 min)
4. Wednesday, Feb 11 at 12:00 PM (30 min)

Which slot works best?
```

**User:** 1

**Step 6 - Create event:**
```bash
TZ="Europe/Stockholm"
TOKEN=$(gcloud auth application-default print-access-token) && \
curl -s -X POST "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1&sendUpdates=all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: fine-pm-em-staff" \
  -d '{
    "summary": "Subledger Updates",
    "description": "Discussion about subledger updates",
    "start": {"dateTime": "2026-02-09T11:00:00", "timeZone": "'"$TZ"'"},
    "end": {"dateTime": "2026-02-09T11:30:00", "timeZone": "'"$TZ"'"},
    "attendees": [{"email": "'"$USER_EMAIL"'"}, {"email": "natemehari@spotify.com"}],
    "conferenceData": {
      "createRequest": {
        "requestId": "meeting-1234567890",
        "conferenceSolutionKey": {"type": "hangoutsMeet"}
      }
    }
  }'
```

**Step 7 - Confirm:**
```
Meeting booked!

**Subledger Updates**
- When: Monday, February 9 at 11:00 AM - 11:30 AM
- Attendees: natemehari@spotify.com (invite sent)
- Google Meet: https://meet.google.com/abc-defg-hij

Nate will receive an email invitation automatically.
```

---

## Example Flow: Name Resolution

**User:** `/book "design review" with Anna 30min early this week`

**Step 1 - Check auth:** → OK

**Step 2 - Detect timezone:** → Europe/Stockholm

**Step 3 - Parse request:**
- Title: "Design Review"
- Attendees: "Anna" → classified as a **name** (capitalized, no @)
- Duration: 30 minutes
- Window: Mon–Wed this week

**Step 3b - BigQuery lookup:**
```bash
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
DATE_SUFFIX=20260208

bq query --use_legacy_sql=false --format=json --max_rows=20 "
SELECT
  c.name, c.email, c.username,
  c.workday.work_role AS job_title,
  c.flattened_organization.squad AS squad,
  c.flattened_organization.product_area AS product_area,
  c.flattened_organization.studio AS studio,
  c.flattened_organization.mission AS mission,
  c.flattened_organization.alliance AS alliance,
  u.flattened_organization.squad AS user_squad,
  u.flattened_organization.product_area AS user_product_area,
  u.flattened_organization.studio AS user_studio,
  u.flattened_organization.mission AS user_mission,
  u.flattened_organization.alliance AS user_alliance
FROM \`spotify-people.spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}\` c
CROSS JOIN (
  SELECT flattened_organization
  FROM \`spotify-people.spotifiers_extended.spotifiers_extended_${DATE_SUFFIX}\`
  WHERE LOWER(email) = LOWER('${USER_EMAIL}')
  LIMIT 1
) u
WHERE LOWER(c.name) LIKE 'anna %'
ORDER BY c.name
LIMIT 20
"
```

→ Returns 3 results

**Step 3c - Compute org distance:**
- Anna Hedin: same studio (distance 4)
- Anna Gorka: same alliance (distance 8)
- Anna Smith: different org (distance 10)

**Step 3d - Present disambiguation (via AskUserQuestion):**
```
Multiple people named "Anna". Closest to you:

1. Anna Hedin (ahedin@spotify.com)
   Senior Engineer · Payments Squad — same studio
2. Anna Gorka (agorka@spotify.com)
   Product Designer · Creator Tools — same alliance
3. Anna Smith (asmith@spotify.com)
   Data Scientist · Ad Platform — different org

Which Anna?
```

**User selects:** 1

**Step 4 onward:** Proceeds with `ahedin@spotify.com` as the attendee (same as the existing flow).

---

## Error Handling

**Calendar scope not configured:**
```
Calendar access not configured. Run this command:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform"

Then try /book again.
```

**Token expired:**
```
Your credentials have expired. Run:

gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform"

Then try /book again.
```

**Cannot access attendee calendar:**
```
Could not check availability for [email].
They may have calendar sharing disabled.

Options:
1. Proceed with booking based on your availability only
2. Ask them to share their calendar with you

Proceed anyway? (yes/no)
```

**Quota project error:**
If you see "requires a quota project" error, ensure the `x-goog-user-project: fine-pm-em-staff` header is included in all API calls.

**BigQuery access denied (name resolution):**
If BigQuery returns a permission error during name resolution, fall back to appending `@spotify.com` to the input and warn the user:
```
Could not look up "Anna" in the directory (BigQuery access denied).
Falling back to anna@spotify.com — if this is wrong, provide the full email.
```

**No BigQuery partition available (name resolution):**
If today's partition doesn't exist, try yesterday's, then 2 days ago. If none exist, fall back to `@spotify.com` append with a warning.

---

## API Reference

**Freebusy Query:**
```
POST https://www.googleapis.com/calendar/v3/freeBusy
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: fine-pm-em-staff
```

**Create Event:**
```
POST https://www.googleapis.com/calendar/v3/calendars/primary/events
  ?conferenceDataVersion=1  (for Meet link)
  &sendUpdates=all          (send invites)
Headers:
  Authorization: Bearer $TOKEN
  x-goog-user-project: fine-pm-em-staff
```

**Update Event (add attendees):**
```
PATCH https://www.googleapis.com/calendar/v3/calendars/primary/events/{eventId}
  ?conferenceDataVersion=1
  &sendUpdates=all
```

**List Events:**
```
GET https://www.googleapis.com/calendar/v3/calendars/primary/events
  ?timeMin=...&timeMax=...&q=search
```
