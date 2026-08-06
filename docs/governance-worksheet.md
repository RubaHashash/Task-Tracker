# Governance Retrospective - AI Assisted Coding

## What I Shared With AI

| Item shared | Module | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---:|---|---|---|---|
| Task Tracker code | 2-5 | Low | The shared material is course toy-project code with no identified secrets, PII, production configuration, or proprietary logic. | Paste only the files or minimal functions relevant to the prompt, after checking for credentials, personal paths, and private comments. | Confirm whether the repository is public and whether any copied files contained untracked secrets or personal information. |
| Test output and stack traces | 2-4 | Medium | Test output is normally non-sensitive, but stack traces can reveal personal filesystem paths, usernames, environment details, source snippets, or accidentally printed values. | Paste a redacted excerpt containing the exception type, relevant application frames, and failing assertion; replace usernames, absolute paths, tokens, and data values with placeholders. | Were absolute paths, usernames, environment variables, request payloads, or secret values present? If none were present, Low may be appropriate. |
| Frontend code | 3 | Low | The frontend is course toy-project code, and the reviewed file contains UI logic and a localhost API address rather than sensitive data or proprietary logic. | Share only the relevant HTML or JavaScript function and replace environment-specific URLs or identifiers with placeholders. | Confirm that the pasted version did not include analytics keys, private service URLs, tokens, or real user content. |
| Dockerfile and CI YAML | 4 | Low | The reviewed configuration describes a course container and test workflow and contains no visible credentials, production infrastructure, or deployment secrets. | Paste a sanitized configuration with registry names, account identifiers, private repository references, secret names, and production endpoints replaced by descriptive placeholders. | Did a different pasted version include private registry details, cloud account IDs, production configuration, or literal secret values? |
| Any real external data used by mistake | N/A | TODO | The row does not identify what data was shared. Real customer data, PII, regulated data, credentials, or unauthorized code would be High, while public non-sensitive data could be Low. | Do not paste raw external data; use fabricated records with the same schema and edge cases, remove direct and indirect identifiers, and verify that no secrets or production values remain. | Specify whether external data was actually shared, its source, whether it was public, whether sharing was authorized, and whether it contained PII, regulated data, credentials, or customer information. |

## What I Received From AI

| Generated thing | Module | Do I understand it line by line? | Action |
|---|---:|---|---|
| Backend models and validators | 2 | TODO | TODO |
| Frontend board and drag-and-drop logic | 3 | TODO | TODO |
| CI workflow | 4 | TODO | TODO |

## Personal AI Usage Rules

| Rule category | Draft rule | Evidence from my notes | What is still vague? | Revised rule |
|---|---|---|---|---|
| What I will never paste | I will never paste raw external data, credentials, tokens, PII, regulated data, customer information, unauthorized code, or production values into an AI tool. | The worksheet identifies these materials as potentially High risk and says to use fabricated records, remove identifiers, and verify that secrets and production values are absent. | The worksheet does not confirm whether external data was actually shared or define how authorization will be checked. | Before pasting anything, I will remove credentials, tokens, direct and indirect identifiers, production values, customer information, regulated data, and code I am not authorized to share. I will replace external data with fabricated records that preserve only the needed schema and edge cases. |
| What I will always verify before accepting | Missing - add course evidence. | The worksheet lists backend models and validators, frontend board and drag-and-drop logic, and the CI workflow, but "Do I understand it line by line?" and "Action" remain TODO. | The notes do not state which checks must pass before accepting AI-generated work. | Missing - add course evidence. |
| How I will record AI contributions | I will record each AI-generated item with its module, whether I understand it line by line, and the action I took. | The "What I Received From AI" table already uses the columns "Generated thing," "Module," "Do I understand it line by line?" and "Action." | The notes do not specify when or where this record must be updated. | For every AI-generated contribution, I will complete all four worksheet fields: generated thing, module, line-by-line understanding status, and action taken. I will not leave the understanding or action fields as TODO. |
