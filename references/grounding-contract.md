# The grounding contract (mikeross's anti-hallucination engine)

This is what makes a mikeross knowledge base trustworthy: **nothing in it is invented.**
It applies to `build` (how notes are written) and `ask` (how questions are answered).
It is **strict by default**; `--light` skips the provenance machinery for casual vaults.

## 1. Every note is traceable
Each atomic note carries frontmatter that pins it to its source:
```yaml
---
source_doc: "<file or chunk it came from>"
source_pages: [96-105]     # the page(s) it draws from, in the source's own numbering
confidence: clean          # clean | noisy   (noisy = OCR/table garble, treat figures with care)
---
```
A note with `confidence: noisy` tags risky figures inline: `⚠️ verify against source`.

## 2. Answers cite or abstain
When answering (`ask`):
- State only what the notes support. Every claim carries its citation — `[[Note]] (p. NNN)`.
- If the answer is **not in the KB**, say exactly that. Do not fill the gap from general
  knowledge. The user would rather hear "the KB doesn't cover this" than a confident guess.
- Any figure from a `noisy` note is flagged `⚠️ verify against source` with the file to check.

## 3. Brutal honesty + escalate (never paper over a gap)
If you *cannot* answer, or you hit a **problem zone** — an un-OCR'd page, unreadable cells,
contradictory figures, any malfunction — do **not** guess. Instead:
1. Say *why* you can't answer ("p. 113 didn't OCR, so the Component-1 budget can't be pulled").
2. Pinpoint the zone (note + page).
3. Append a task to `_Review Queue.md`:
   `- [ ] [Ask] <topic> — <note> p.<NNN> — <what's broken>`
4. Surface the same flag inline in your answer.

This closes a loop: `ask` flags broken source → a later `build`/ingest re-OCRs or fixes
those exact pages → the KB gets stronger over time.

## 4. When in doubt, ask
Placement, naming, "is this the figure you meant", strict-vs-light — when the right call
depends on the user's knowledge, ask one well-prepared question rather than assume. A wrong
guess silently propagates; a question costs one turn.

## `--light` mode
Drops `source_pages`/`confidence` frontmatter and the cite-or-abstain rule — just clean,
linked notes. Use it for personal/low-stakes vaults. The structure and graph still work;
only the provenance guarantees are off. Say so when you use it, so the user knows the KB
is no longer self-verifying.
