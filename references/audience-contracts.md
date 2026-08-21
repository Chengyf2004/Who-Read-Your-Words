# Audience Contracts

Read this reference when the writing mode is ambiguous, several audiences are mixed, or it is unclear whether history belongs in the artifact.

## Mode contracts

| Mode | Reader need | Content that belongs | Process boundary |
|---|---|---|---|
| State | Understand, evaluate, use, or maintain the current subject | Current capabilities, instructions, interfaces, examples, limitations, and reader-relevant rationale | Editing requests and superseded approaches stay outside the artifact |
| Change | Understand what changed and its impact | Before/after behavior when useful, motivation, scope, compatibility, migration, and verification relevant to the change | Assistant corrections and conversational detours are not project history |
| Decision | Evaluate why a choice was or should be made | Context, options, evidence, decision, consequences, risks, and accountability | Include only deliberation that serves the record's readers |
| Direct | Receive an answer, update, request, or call to action | Shared context, necessary acknowledgement, result, evidence, and next action | Internal mechanics belong only when disclosure is required or useful to this recipient |

## Common routing

- README, user guide, API/reference documentation, architecture overview, landing page, and UI copy usually use **state**.
- PR title/body, commit message, changelog, release note, and migration guide usually use **change**.
- ADR, proposal, postmortem, audit response, and review response usually use **decision**.
- Email, support reply, stakeholder update, announcement, and completion response usually use **direct**.

These are defaults, not name-based guarantees. Infer the actual reader goal from the request and artifact.

## Reader-relevant negatives

A negative statement belongs when it changes a reader decision or action. Unsupported environments, incompatibilities, deprecations, security restrictions, and explicit non-goals can be essential. A rejected idea or correction does not become reader-relevant merely because it was prominent in the task conversation.

## Multiple audiences

When one artifact must serve several audiences, make the boundaries visible with sections or separate artifacts. Do not silently switch from end-user guidance to reviewer commentary or task reporting. Prefer separate deliverables when the audiences require different context or levels of disclosure.

## Final sentence test

For each sentence, identify:

1. who benefits from it;
2. what the reader can do or understand because of it;
3. where its facts come from;
4. whether its references make sense without hidden context;
5. whether the selected genre normally carries that information.

If no intended reader benefits, relocate the sentence to the appropriate process record or remove it.

