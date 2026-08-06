# My Personal AI Coding Playbook

## 1. When I reach for AI first

- I use AI first when I need to understand an unfamiliar codebase. The project map helped me find the real frontend path before I started making changes.
- I use it to draft structured work such as models, tests, documentation, and CI files, especially when I can give it the actual files and clear constraints.
- I use it during debugging after I have a failing test, error message, or reproducible behavior to share.

## 2. When I do not reach for AI

- I do not use AI to make the final decision on architecture, security findings, or whether a change is ready. Those judgments stay with me.
- I do not ask it to replace hands-on testing. Using the frontend myself exposed an edit-modal bug that code review alone missed.
- I do not use real private data just to make a prompt more realistic; I can use sanitized or fabricated data instead.

## 3. My non-negotiables

- I will not paste credentials, tokens, `.env` contents, personal information, customer data, or production logs into an AI tool.
- I will check that a requested change was actually applied. A diff or code block in the chat does not mean the repository changed.
- I own the final result. AI can draft and explain, but I must understand, verify, and accept the work myself.

## 4. My review rules

- I read the complete diff and confirm that only the intended files and behavior changed.
- I run the relevant tests and, for important rules, use a break test to prove that the tests can catch a real defect.
- I verify behavior at the right level: API checks for backend work, the browser for frontend work, and actual commands for CI, Docker, or documentation links.

## 5. What I am still figuring out

- I am still learning when editor assistance is enough and when a repo-level or terminal agent is worth the wider access.
- I am still working out how much AI-generated code I can review carefully in one change without missing details.
- I want a consistent way to record what AI contributed, what I changed, and what evidence made me accept it.

## Decision Card

AI-Assisted Coding - Module 5 Prompt Library
- For a new feature I reach for: Claude Code, starting with a repository map and a small, scoped plan.
- For a code review I reach for: Codex App in read-only mode, followed by my own diff review and verification.
- For debugging I reach for: Claude Code with the exact error, failing test, or reproducible behavior.
- For infrastructure I reach for: Claude Code in the terminal, with every generated file reviewed and every command verified.
- I will never paste credentials, tokens, `.env` contents, personal information, customer data, or production logs into an AI tool.
- My one rule is: AI can propose the work, but I do not accept it until I have inspected and tested it.
