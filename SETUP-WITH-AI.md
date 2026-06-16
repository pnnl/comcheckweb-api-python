# Set Up a COMcheck API Project with an AI Assistant

This guide is for people who **don't write code**. You'll use an AI coding
assistant — **Claude Code**, **GitHub Copilot**, or **OpenAI Codex** — to do
all the technical work for you. Your job is just to:

1. Open your AI assistant.
2. Copy the prompt below and paste it in.
3. Answer a couple of simple questions when the assistant asks.

The AI will create a fresh project folder, install the COMcheck API library,
and set up the "Skill" that teaches the AI how to use the library correctly.

---

## Before you start

You need two things:

### 1. A COMcheck API Key (free)

1. Go to **https://comcheck.energycode.pnl.gov** and log in (or register).
2. Click your **username** in the left-side menu.
3. Choose **Settings** → **Developer Setting**.
4. Click **Generate**, then **copy the token immediately**.

> ⚠️ The token is shown **only once**. Paste it somewhere safe (a password
> manager or a note) before leaving the page. If you lose it, just generate
> a new one.

### 2. An AI coding assistant, already open

- **Claude Code** — in your terminal, or the VS Code / JetBrains extension.
- **GitHub Copilot** — the Chat/Agent panel in VS Code.
- **OpenAI Codex** — the Codex CLI or extension.

Have the AI assistant open and ready to chat. Then continue below.

---

## Step 1 — Copy this prompt to your AI assistant

Select everything inside the box and paste it into your AI assistant's chat.

> Please set up a brand-new Python project for me that uses the **COMcheck
> API** library. I am not a programmer, so do every step for me and explain
> what's happening in plain language. Specifically:
>
> 1. Create a new project folder called `comcheck-project` and open it.
> 2. Make sure Python 3.12 or newer is available. If a tool called `uv` is
>    installed, use it; otherwise use plain `pip` and a virtual environment.
>    Pick whichever works and tell me what you chose.
> 3. Install the library from PyPI: the package name is **`comcheck-api`**.
> 4. After it's installed, run the command **`comcheck-api install-skill`**
>    inside the project folder. This installs the bundled AI "Skill" so you
>    (the assistant) know how to use the library correctly. Confirm that it
>    created a `.claude/skills/comcheck-api/` folder (and/or
>    `.agents/skills/comcheck-api/`).
> 5. Create a file named `.env` in the project folder with this line, and
>    pause to let me paste in my real key:
>    `COM_API_KEY=<I will paste my key here>`
> 6. Add `.env` to a `.gitignore` file so my key never gets shared.
> 7. Write a small test script called `check_setup.py` that loads the key
>    from `.env`, creates a `COMcheckClient`, and prints a friendly message
>    confirming the library is installed and the key was read. Run it and
>    show me the output.
>
> Go one step at a time. Stop and ask me whenever you need my API key or a
> decision from me.

---

## Step 2 — Paste your API key when asked

When the assistant pauses at the `.env` step, paste the key you copied
earlier so the line looks like:

```
COM_API_KEY=abc123yourrealtokenhere
```

Save the file (the assistant can do this for you).

---

## Step 3 — Confirm it worked

When the assistant runs `check_setup.py`, you should see a message like
"COMcheck API is installed and your key was loaded." If you see an error
instead, paste the error back to the assistant and ask it to fix it — that's
exactly what these tools are good at.

---

## What you end up with

A folder named `comcheck-project` containing:

- The **`comcheck-api`** library, installed and ready.
- A **Skill** folder (`.claude/skills/comcheck-api/` and/or
  `.agents/skills/comcheck-api/`) that makes your AI assistant an expert on
  this library.
- A **`.env`** file holding your API key (kept private by `.gitignore`).
- A working **`check_setup.py`** test script.

From here you can ask your AI assistant things like *"Run a COMcheck
compliance simulation for a small office building"* and it will use the
installed Skill to write the right code for you.

---

## Reference (for the curious)

The whole setup boils down to these commands, which the AI runs for you:

```bash
# Install the library
pip install comcheck-api          # or: uv add comcheck-api

# Install the AI Skill into this project
comcheck-api install-skill        # both Claude & Codex
# comcheck-api install-skill --claude   # Claude Code only
# comcheck-api install-skill --codex    # OpenAI Codex only
```

- Requires **Python 3.12+**.
- Full docs: **https://pnnl.github.io/comcheckweb-api-python/**
- Get an API key: **https://comcheck.energycode.pnl.gov**
