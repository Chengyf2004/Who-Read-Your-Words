# Who Reads Your Words?

[简体中文](README.md) | English

[![skills.sh](https://skills.sh/b/chengyf2004/who-reads-your-words)](https://skills.sh/chengyf2004/who-reads-your-words/who-reads-your-words)

## Have you ever run into either of these?

**A weekly report turns into a debugging log.** You ask an AI to turn a week of issues, commits, and investigation notes into a report for your manager. You want the manager to see: “Fixed intermittent login-service timeouts. The root cause was a conflict between the connection-pool configuration and retry policy; the fix is deployed and the service is stable.” The AI instead writes: “On Monday, we first tried optimizing database indexes, with no effect. On Tuesday, changing the connection-pool settings introduced a new error. On Wednesday, we discarded the original diagnosis and investigated the retry policy instead. At a later request, some investigation details were removed...” A report intended to communicate final progress becomes a trial-and-error transcript containing incorrect diagnoses, temporary actions, and even editing instructions.

**Deletion turns into repetition.** You ask an AI to remove a rejected Redis proposal from a technical document because its final readers have no reason to know it ever existed. The AI removes the original section but renames the document “System Design (Without Redis),” opens with “This document does not discuss Redis,” and adds a section titled “Why This Document Does Not Discuss Redis.” Redis disappears from the design but becomes the document's most visible topic.

Both outputs follow the instruction literally, yet lose sight of the document's actual readers. False starts, editing instructions, and rejected material are internal inputs that help complete a task. When they cross the audience boundary into the delivered artifact, the result is **internal process leakage**.

`who-reads-your-words` starts by asking: **Who will read these words, and what does that reader actually need to know?**

`who-reads-your-words` is a Codex skill for keeping outward-facing text aligned with the people who will actually read it.

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

Install it globally for Codex with the [skills CLI](https://skills.sh/docs/cli):

```bash
npx skills add Chengyf2004/Who-Reads-Your-Words --skill who-reads-your-words --agent codex -g -y
```

Or use GitHub CLI:

```bash
gh skill install Chengyf2004/Who-Reads-Your-Words who-reads-your-words --agent codex --scope user
```

## Use

Invoke the skill explicitly when drafting an artifact:

```text
Use $who-reads-your-words to write a README for first-time users of this project.
```

It can also review existing text:

```text
Use $who-reads-your-words to review this PR description for audience mismatch and task-process leakage.
```

## Audit existing text

The included linter provides a deterministic first pass for Markdown and plain text:

```bash
python skills/who-reads-your-words/scripts/audit_external_text.py README.md --profile state
```

Select `state`, `change`, `decision`, or `direct` to match the artifact. Errors identify strong audience-boundary failures. Warnings require a reader-value decision and are not automatic deletion instructions.

Use `--fail-on warning` for a stricter CI gate or `--verbose` to display the flagged source lines.

## Validate

Run the audit tests with Python's standard library:

```bash
python -m unittest discover -s skills/who-reads-your-words/scripts -p "test_*.py" -v
```

The test cases cover clean current-state writing, reader-relevant limitations, project change records, direct acknowledgements, hidden conversation dependencies, migration sections, fenced examples, and process-oriented headings.

## Repository structure

```text
who-reads-your-words/
├── README.md
├── README.en.md
├── LICENSE
├── .gitignore
└── skills/
    └── who-reads-your-words/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   └── audience-contracts.md
        └── scripts/
            ├── audit_external_text.py
            └── test_audit_external_text.py
```

## License

This project is licensed under the [MIT License](LICENSE).

## Limits

The linter detects textual signals; it cannot determine audience relevance with complete semantic accuracy. Profile selection and the skill's audience tests remain the source of judgment. The audit reports possible problems without rewriting or deleting content automatically.
