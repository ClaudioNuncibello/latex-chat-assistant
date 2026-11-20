---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to `docs/handoff.md` in the repository (create `docs/` if missing), overwriting the previous one: git history keeps the older handoffs. The file is committed and pushed with the repo, so collaborators and their agents read it too. Write it in the language the user is writing in.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

The document ends up in the git history, so redact any sensitive information, such as API keys, tokens, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
