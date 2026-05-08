name: notebooklm
description: >
  Query Google NotebookLM notebooks using the Codex Chrome extension.
  Trigger when the user mentions NotebookLM, asks to query their notebooks,
  wants source-grounded answers from uploaded documents, shares a NotebookLM
  URL, or uses phrases like "ask my NotebookLM", "check my docs",
  "query my notebook". Requires the Chrome extension to be connected.
  Do NOT trigger for general web searches, code questions, or tasks unrelated
  to the user's NotebookLM document collections.
---

# NotebookLM Skill for Codex

Interact with Google NotebookLM through the Codex Chrome extension. Codex uses
your authenticated Chrome browser to query notebooks and retrieve source-grounded
answers from Gemini. No Playwright, no Python dependencies, no cookie management.

## Prerequisites

- Codex Chrome extension installed and connected
- User logged into Google in Chrome
- At least one NotebookLM notebook with uploaded sources

## Quick Start

```
@Chrome open https://notebooklm.google.com
```

Wait for the page to load, then ask a question.

## Notebook Library

Maintain a notebook library in a local file `data/library.json` within the skill
directory. If the file does not exist, create it on first use.

Schema:
```json
{
  "notebooks": [
    {
      "id": "short-kebab-id",
      "name": "Display Name",
      "url": "https://notebooklm.google.com/notebook/XXXX",
      "description": "What this notebook contains",
      "topics": ["topic1", "topic2"],
      "use_cases": ["when to query this notebook"]
    }
  ],
  "active_notebook_id": "short-kebab-id"
}
```

### Adding a Notebook

When the user wants to add a notebook:

1. If the user provides a NotebookLM URL, open it first and ask the notebook
   what it contains:
   ```
   @Chrome open [URL]
   ```
   Then query: "What is the content of this notebook? What topics are covered?
   Provide a brief overview."

2. Use the discovered (or user-provided) information to add the entry to
   `data/library.json`.

3. NEVER guess descriptions or topics. If in doubt, query the notebook first.

### Listing Notebooks

Read `data/library.json` and display the list with name, topics, and description.

### Selecting a Notebook

If the user specifies a topic, search the library for the best-matching notebook
by checking topics, description, and name. If ambiguous, ask the user to clarify.

If the user provides a URL directly, use that URL regardless of the library.

If no notebook is specified and an active notebook is set, use the active one.

If no notebook is specified and none is active, list available notebooks and ask.

## Querying a Notebook

### Step 1: Open the notebook

```
@Chrome open [notebook URL]
```

Wait for the page to fully load. The NotebookLM interface shows a text input
area at the bottom of the page.

### Step 2: Ask the question

Locate the query input (a textarea at the bottom of the chat interface). Type
the user's question into it and submit by pressing Enter.

Compose the question to be self-contained. Each query to NotebookLM is
independent with no conversation memory. Include relevant context from the
user's original request.

### Step 3: Wait for the response

NotebookLM streams its response. Wait until the response text is fully
generated and stable. The response area shows the answer with inline citations
referencing the uploaded source documents.

### Step 4: Read the answer

Read the full response including all citations. NotebookLM answers are grounded
ONLY in the uploaded source documents, which drastically reduces hallucinations.

### Step 5: Follow-up if needed

BEFORE responding to the user:

1. Compare the answer to the user's original question.
2. Identify any gaps or unclear points.
3. If information is incomplete, ask a follow-up question in the same notebook.
4. Repeat until the answer is comprehensive.
5. Synthesize all answers into a single coherent response.

## Workflow Decision Tree

```
User mentions NotebookLM or asks about their documents
  |
  ├─ User provides URL? → Use that URL directly
  ├─ User specifies topic? → Search library for best match
  ├─ Active notebook set? → Use active notebook
  └─ None of the above? → List notebooks, ask user to pick
  |
  ├─ Notebook not in library? → Query it for content, then add to library
  |
  └─ Ready to query
      |
      ├─ @Chrome open notebook URL
      ├─ Type question in input, submit
      ├─ Wait for full response
      ├─ Read answer with citations
      ├─ Need follow-up? → Ask another question
      └─ Synthesize and respond to user
```

## Important Notes

- **Source-grounded answers:** NotebookLM responses are based exclusively on the
  uploaded documents. If the documents don't contain the answer, NotebookLM will
  say so. Do NOT supplement with external knowledge unless the user asks.

- **No conversation memory:** Each question is independent. Always include full
  context in every question you send to NotebookLM.

- **Rate limits:** Free Google accounts are limited to approximately 50 queries
  per day. Be mindful of this when planning follow-up questions.

- **Citations:** Always include source citations from NotebookLM in your response
  to the user. This is the key value of using NotebookLM over a regular LLM.

- **Privacy:** NotebookLM content comes from the user's own uploaded documents.
  Treat all retrieved content as private and confidential.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome extension disconnected | Ask user to check extension icon in Chrome toolbar, reconnect if needed |
| Redirected to Google login | User needs to log into Google in Chrome, then retry |
| Notebook URL not found | Verify URL with user, check library.json for correct URL |
| Empty response | Retry the question, possibly rephrased. Notebook may have limited sources |
| Rate limited (50/day) | Wait for reset or suggest user switch Google account |

## Differences from the Original PleasePrompto Skill

This skill replaces the original Python/Patchright-based implementation. Key
changes:

- No Playwright or Patchright required
- No virtual environment or Python dependencies
- No cookie/state management (Chrome handles auth)
- No stealth/anti-detection measures needed
- Browser automation handled by Codex Chrome extension
- Library management simplified to a JSON file
- ~50 lines of instructions instead of ~1500 lines of Python

## File Structure

```
.agents/skills/notebooklm/
├── SKILL.md              # This file
├── data/
│   └── library.json       # Notebook library (auto-created)
└── references/
    └── usage_patterns.md  # Extended examples (optional)
```
