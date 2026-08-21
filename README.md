# Who Reads Your Words?

`who-read-your-words` is a Codex skill for keeping outward-facing text aligned with the people who will actually read it.

It prevents task instructions, revision chatter, rejected ideas, and agent activity from leaking into artifacts that have a different audience. A README stays a README, a pull request describes the project change, and a direct update can still tell the requester what was completed.

## What it does

Before drafting, the skill establishes an internal audience contract:

- who will read the text;
- which channel and artifact type will carry it;
- what the reader needs to understand or do;
- which context the reader can reasonably possess;
- whether the artifact represents current state, change, decision history, or direct conversation.

Task instructions are treated as control information rather than automatic document content. The skill then builds an audience view from verified subject facts and applies two checks before delivery:

- **Orphan-reader test:** Can the intended reader understand and use the text without hidden task context?
- **Counterfactual test:** For current-state writing, would every sentence still belong if the subject had always been in its present state?

## Writing modes

| Mode | Typical artifacts | What the reader needs |
|---|---|---|
| `state` | README, user guide, API docs, landing page, UI copy | The current subject and its actionable boundaries |
| `change` | PR, commit, changelog, release note, migration guide | What changed, why it matters, and its impact |
| `decision` | ADR, proposal, postmortem, review response | Context, evidence, alternatives, rationale, and consequences |
| `direct` | Email, support reply, stakeholder update, completion report | A useful answer, result, or next action in shared context |

Negative statements are not banned. Limitations, incompatibilities, security boundaries, and deprecations belong when they change a reader decision. The distinction is whether the information serves the audience, not whether its wording is negative or historical.

## Install

Clone the repository into the Codex skills directory.

macOS or Linux:

```bash
git clone https://github.com/Chengyf2004/who-read-your-words.git ~/.codex/skills/who-read-your-words
```

Windows PowerShell:

```powershell
git clone https://github.com/Chengyf2004/who-read-your-words.git "$env:USERPROFILE\.codex\skills\who-read-your-words"
```

## Use

Invoke the skill explicitly when drafting an artifact:

```text
Use $who-read-your-words to write a README for first-time users of this project.
```

It can also review existing text:

```text
Use $who-read-your-words to review this PR description for audience mismatch and task-process leakage.
```

## Audit existing text

The included linter provides a deterministic first pass for Markdown and plain text:

```bash
python scripts/audit_external_text.py README.md --profile state
```

Select `state`, `change`, `decision`, or `direct` to match the artifact. Errors identify strong audience-boundary failures. Warnings require a reader-value decision and are not automatic deletion instructions.

Use `--fail-on warning` for a stricter CI gate or `--verbose` to display the flagged source lines.

## Validate

Run the audit tests with Python's standard library:

```bash
python -m unittest discover -s scripts -p "test_*.py" -v
```

The test cases cover clean current-state writing, reader-relevant limitations, project change records, direct acknowledgements, hidden conversation dependencies, migration sections, fenced examples, and process-oriented headings.

## Repository structure

```text
who-read-your-words/
├── README.md
├── SKILL.md
├── .gitignore
├── agents/
│   └── openai.yaml
├── references/
│   └── audience-contracts.md
└── scripts/
    ├── audit_external_text.py
    └── test_audit_external_text.py
```

## Limits

The linter detects textual signals; it cannot determine audience relevance with complete semantic accuracy. Profile selection and the skill's audience tests remain the source of judgment. The audit reports possible problems without rewriting or deleting content automatically.

