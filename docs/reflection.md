# Reflection

The main tool I used across this mid-course branch was Claude Code, as the
sole AI assistant for the whole workflow: reviewing the existing FastAPI +
vanilla JS Task Tracker before touching anything, drafting the due-date
architecture decision, implementing the backend model/storage/filter
changes, building the frontend modal/card/toolbar work, debugging a real
bug, proposing and writing the pytest tests, and refactoring the frontend's
filter-building code. Alongside it, I relied on `pytest` after nearly every
step to check nothing regressed, and on `curl`/`Invoke-RestMethod` for
live API checks, since no automated browser tool was available in this
environment — verification stayed at the API level more than I'd have liked.

One moment where AI clearly helped: before any code changed, I had it
produce a full implementation map of the existing project. That single step
caught that the frontend file actually lived at `app/frontend/index.html`,
not `frontend/index.html` as I'd assumed — a small thing, but it anchored
every request after that to the right file instead of drifting. Later, when
I asked for due-date test coverage, it didn't just write the 8 tests I
listed — it added a ninth "break test" for the exact `<` vs `<=` boundary on
the overdue rule, which is precisely the kind of off-by-one I wouldn't have
thought to ask for explicitly.

One moment it slowed me down: I asked it to extend `GET /tasks` with search
and assignee filters, and it came back with a diff, pseudocode, and curl
examples — but hadn't actually written any of it to the files. I only caught
this because I asked "you added the apis in the project?" a turn later. It's
a small gap, but it cost a full extra round trip, and it's exactly the kind
of thing that's easy to miss if you don't double-check.

The clearest place my own review changed the result was a bug I hit using
the app directly, not through any script: I couldn't add a due date through
the edit modal. That forced a real investigation — it turned out the modal
was resending the task's unchanged status on every edit, which collided with
a backend rule that (correctly) rejects a status "transition" to itself. My
report is what surfaced it; without actually using the running app instead
of just trusting the code review, that bug would have shipped.

What I'm taking from this: verify by using the thing, not just reading the
diff, and don't assume "shown" means "applied."
