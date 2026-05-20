# Options for Building an AI Layer on Top of `comcheck_api`

The package is published on PyPI; users `pip install` it regardless. The
AI layer is really about *how to deliver SDK knowledge to whatever model
the user is already using*. The options below are organized from
lightest-touch to most product-heavy.

## A. Ship-with-the-package options (no AI hosting on your side)

These add metadata to the existing PyPI package. Users bring their own
AI client.

### 1. `llms.txt` + curated context files

Ship a top-level `llms.txt` and a `docs/llms-full.txt` (now a
quasi-standard) plus a `CLAUDE.md` / `cursor.rules` in the package. Any
AI assistant the user already runs (Claude Code, Cursor, Copilot,
ChatGPT) can ingest these.

- **Effort**: lowest — it's just structured docs.
- **Pros**: works everywhere, no infra, no API costs to you.
- **Cons**: discovery depends on the user's tool reading those files.

### 2. Claude Skill (Anthropic Skills)

Package the SDK reference + golden examples as a `.skill` — distributed
via a public skills repo or marketplace. Users invoke it from Claude
Code / claude.ai / Agent SDK.

- **Effort**: low — mostly authoring `SKILL.md` and curating examples.
- **Pros**: official distribution channel, model loads it on-demand,
  no inference cost to you.
- **Cons**: Claude-only ecosystem.

### 3. MCP Server bundled in the PyPI package

Add a `comcheck-mcp` entry point. Users add one line to their
`claude_desktop_config.json` / `mcp.json` and get tools like
`search_sdk_docs`, `lookup_type(name)`, `generate_project_skeleton`,
`validate_generated_code`. Works with Claude Desktop, Claude Code,
Cursor, Windsurf, etc.

- **Effort**: medium — write the MCP server, but the SDK is already
  there to wrap.
- **Pros**: protocol is multi-client; you control retrieval and
  validation; can include a *runtime check* tool (`validate_code`) that
  imports the user's draft and reports errors — huge quality boost vs.
  plain RAG.
- **Cons**: users need an MCP-capable host.

### 4. Custom GPT / Claude Project / Gemini Gem

Upload SDK docs + examples into a hosted assistant on
claude.ai/chatgpt/gemini. Share a public link.

- **Effort**: lowest — drag-and-drop docs.
- **Pros**: zero infra, instantly shareable.
- **Cons**: per-platform; users need that platform's subscription;
  you don't control the retrieval.

## B. Embedded-in-the-package options (you ship the AI logic, user brings keys)

### 5. CLI assistant inside the package

`comcheck-api ai "build a 5000 sqft office in Seattle"` → calls
Claude/OpenAI with bundled SDK context, returns runnable Python. User
sets their own `ANTHROPIC_API_KEY`.

- **Effort**: medium.
- **Pros**: zero hosting cost to you; users get a turnkey experience
  after `pip install`.
- **Cons**: you pick a model vendor (or support several).

### 6. Python library API

```python
from comcheck_api.ai import Assistant
asst = Assistant(provider="anthropic")
code = asst.generate("3-story office, ASHRAE 90.1-2019, two HVAC units")
```

- **Effort**: medium; same as #5 but as an importable surface for
  power users / notebooks.
- **Pros**: composable inside user pipelines.
- **Cons**: same vendor-choice question.

## C. Hosted product options (you run inference)

### 7. Web app / SaaS

Chat UI at e.g. `ai.comcheck.dev`. Generates code, optionally runs the
simulation server-side and shows the report.

- **Effort**: high — UI, auth, billing, infra.
- **Pros**: full control over UX, can monetize, can pre-run simulations
  and show results visually (the highest-value moment for COMcheck
  users).
- **Cons**: ops burden, you pay for inference unless you charge.

### 8. Hosted API endpoint

You run a single REST endpoint (`POST /generate`) that takes a
natural-language prompt and returns SDK code. Other tools wrap it.

- **Effort**: medium-high.
- **Pros**: lets third parties build UIs on top.
- **Cons**: needs a billing / quota story.

### 9. IDE extension (VS Code / JetBrains)

Targeted assistant tuned for COMcheck — autocomplete, inline "build
envelope" snippets, error explanations.

- **Effort**: high (extension dev + AI plumbing).
- **Pros**: lives where users actually code.
- **Cons**: per-IDE work; arguably duplicates Copilot/Cursor.

## D. Model-training options (rarely worth it for a single SDK)

### 10. Fine-tuned small model on HuggingFace

- **Effort**: high; needs a real eval set.
- **Pros**: cheap inference at scale.
- **Cons**: maintenance every time the SDK changes; modern frontier
  models with good context already match or beat fine-tuned small
  models on tasks like this. Skip unless you have a specific reason.

## Recommendation

For the highest leverage-to-effort ratio for a public release, a
**layered combo**:

1. **#1 `llms.txt`** — free, immediate, helps every tool.
2. **#3 MCP server** — the real product; gives users a "smart
   pair-programmer" with type-aware tools and code validation, and
   works in their existing AI clients.
3. **#2 Claude Skill** — same content repackaged for the Skills
   marketplace, for discovery.

Skip the hosted product (#7) until there's real demand — running it
costs more than it's likely to return at the size of the COMcheck SDK
user base, and you'd be competing against general-purpose AI coding
assistants.
